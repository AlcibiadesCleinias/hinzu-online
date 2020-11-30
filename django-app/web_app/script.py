import os
import sys

import numpy as np
import pickle

from glob import glob

import torch
import torch.nn as nn
from torchvision import models
from torchvision import transforms

import PIL
from PIL import Image, ImageOps, ImageFont, ImageDraw

import cv2

from scipy.spatial.distance import cosine

from .ml.models import BeheadedDenseNet121, calc_embed, upload_model
from .ml.hnsw_wrapper import Index


NN_APPLIER = None

HNSW_INDEX = {}
FILES_MAPPING = {}
EMBEDDINGS = {}

def preprocess(app):
    global NN_APPLIER, EMBEDDINGS
    model_name = app.NN_APPLIER_NAME
    print('try upload model {}'.format(model_name))
    NN_APPLIER = upload_model(model_name).train(False)
    dim = NN_APPLIER.output_embeddings_shape()
    print('model is created')

    print('build all available search indexes')

    data_path = app.DATA_PATH

    for d in os.listdir(data_path):
        if not os.path.isdir(os.path.join(data_path, d)):
            continue
        path2emb = os.path.join(data_path, d, 'embeds.npy')
        path2index = os.path.join(data_path, d, 'hnsw.zip')
        if os.path.exists(path2emb):
            print('found embeds.npy (row images embeddings) for domain {}'.format(d))
            embs = {k:v for k,v in np.load(path2emb, allow_pickle=True)}
            EMBEDDINGS[d] = embs
            if os.path.exists(path2index):
                print('also found hnsw.zip file (hnsw index) for domain {}'.format(d))
                index = Index(space='cosine', dim=dim)
                index.load_index(path2index)
                HNSW_INDEX[d] = index

    print('search indexes are uploaded')


def calc_exact_top(e : 'numpy.ndarray', embeds : dict, top : int):
    diffs = {}

    for k in embeds.keys():
        diffs[k] = cosine(embeds[k],e)
    l = list([(k,diffs[k]) for k in diffs])
    l.sort(key=lambda x:x[1])
    return l[:top]


def calc_hnsw_top(e : 'numpy.ndarray', index : Index, top : int):
    labels, distances = index.knn_query([e], k=top)
    return [l[0] for l in labels]


def find_similar(app, filename, domain='movies', top_size=1):
    e = calc_embed(NN_APPLIER, filename)
    if domain in HNSW_INDEX:
        assert top_size == 1
        index = HNSW_INDEX[domain]
        top = calc_hnsw_top(e, index, top_size)
        return os.path.join(app.DATA_PATH, domain, 'images', top[0]), e
    elif domain in EMBEDDINGS:
        embeddings = EMBEDDINGS[domain]
        top = calc_exact_top(e, embeddings, top_size)
        return os.path.join(app.DATA_PATH, domain, 'images', top[0][0]), e
    else:
        assert False, 'Found bad domain: {}'.format(domain)


class ImageTemplate():
    '''Create concated image via templates.'''

    def __init__(self, path2original, path2similar):
        if os.path.exists(path2original) and os.path.exists(path2original):
            self.path2original = path2original
            self.path2similar = path2similar
        else:
            raise NameError('invalid original and similar paths.')



    def resize_image(self, image, xborder, yborder, mode=None):
        '''Resize image for fixed borders.

        param mode:
            'as_borders': resize to borders.
            None: resize in order to satisfy one border,
            the second mb less.
        '''

        if mode == 'as_borders':
            return cv2.resize(image, (xborder, yborder), interpolation=cv2.INTER_CUBIC)

        kx = image.shape[1]/xborder
        if yborder >= image.shape[0]/kx:
            # expand with x (width)
            return cv2.resize(image, (xborder, int(image.shape[0] / kx)), interpolation=cv2.INTER_CUBIC)
        else:
            # expand with y (height)
            ky = image.shape[0]/yborder
            return cv2.resize(image, (int(image.shape[1] / ky), yborder), interpolation=cv2.INTER_CUBIC)


    def overlay_image(self, background, img_2_put, x_offset, y_offset):
        '''Overlaying img_2_put on background.'''

        assert background.shape[2] == 3, 'This func is not ready to put on background...'

        if img_2_put.shape[2] == 3:  # no alpha chanel
            background[y_offset:y_offset+img_2_put.shape[0],
                       x_offset:x_offset+img_2_put.shape[1]] = img_2_put
            return background

        y1, y2 = y_offset, y_offset + img_2_put.shape[0]
        x1, x2 = x_offset, x_offset + img_2_put.shape[1]
        alpha_s = img_2_put[:, :, 3] / 255.0
        alpha_l = 1.0 - alpha_s
        for c in range(0, 3):
            background[y1:y2, x1:x2, c] = (alpha_s * img_2_put[:, :, c] +
                                           alpha_l * background[y1:y2, x1:x2, c])
        return background


    def rotate_image(self, mat, angle):
        '''Rotates an image (angle in degrees) and expands image to avoid cropping'''

        height, width = mat.shape[:2] # image shape has 3 dimensions
        image_center = (width/2, height/2) # getRotationMatrix2D needs coordinates in reverse order (width, height) compared to shape

        rotation_mat = cv2.getRotationMatrix2D(image_center, angle, 1.)

        # rotation calculates the cos and sin, taking absolutes of those.
        abs_cos = abs(rotation_mat[0,0])
        abs_sin = abs(rotation_mat[0,1])

        # find the new width and height bounds
        bound_w = int(height * abs_sin + width * abs_cos)
        bound_h = int(height * abs_cos + width * abs_sin)

        # subtract old image center (bringing image back to origo) and adding the new image center coordinates
        rotation_mat[0, 2] += bound_w/2 - image_center[0]
        rotation_mat[1, 2] += bound_h/2 - image_center[1]

        # rotate image with the new bounds and translated rotation matrix
        rotated_mat = cv2.warpAffine(mat, rotation_mat, (bound_w, bound_h))
        return rotated_mat


    def overlay_on_black_vertical(self, image, y, area=0.65):
        '''
        Check if vertical, and draw on black background with y param heigh if not &
        also check if area on this background is more then > area param or cut some
        pie & resize.
        '''

        if image.shape[0] >= image.shape[1]:  # image already vertical
            return image

        assert image.shape[0] <= y, 'image.shape[0] (y) bigger y param of func.'
        # check & pie cut
        if image.shape[0] / y < area:
            a = area * y * image.shape[1]
            prev_x = image.shape[1]
            x_to_cut = (a * image.shape[1] - image.shape[0]*image.shape[1]**2) / (2*a)
            image = image[:, int(x_to_cut) : int(image.shape[1]-x_to_cut), :]
            image = self.resize_image(image=image, xborder=prev_x, yborder=int(1e+8), mode=None)
        background = np.zeros((y, image.shape[1], 3))
        x_offset = 0
        y_offset = int((y - image.shape[0])/2)
        background = self.overlay_image(background, image, x_offset, y_offset)
        return background.astype('uint8')


    def to_vertical_concated(self, path2combined):
        '''Create just concated image & save in path2combined.'''

        original = cv2.imread(self.path2original)
        similar = cv2.imread(self.path2similar)

        images = [original, similar]
        w_min = min(im.shape[1] for im in images)
        im_list_resize = [cv2.resize(im, (w_min, int(im.shape[0] * w_min / im.shape[1])), interpolation=cv2.INTER_CUBIC)
                              for im in images]
        im_v_resize = cv2.vconcat(im_list_resize)

        cv2.imwrite(path2combined, im_v_resize)
        return im_v_resize.shape


    def to_movie(self, path2combined, movie_name=None):
        '''Create movie image & save in path2combined.'''

        width = 1080  # bg settings
        height = 1920
        path2background = os.path.join('web_app/static/web_app/images/', 'background_movie_img.png')
        path2font = os.path.join('web_app/static/web_app/webfonts/', 'SpecialElite.ttf')
        assert os.path.exists(path2background) and os.path.exists(path2font), \
               'invalid background or font paths.'

        background = cv2.imread(path2background)
        similar = cv2.imread(self.path2similar)
        original = cv2.imread(self.path2original)

        # put movie image
        img_2_put = self.resize_image(similar, 1000, 550, mode='as_borders')
        x_offset = 40
        y_offset = 1100
        background = self.overlay_image(background, img_2_put, x_offset, y_offset)

        # put original image
        original_yborder = 600  # max values
        original_xborder = 600
        img_2_put = self.resize_image(original, original_xborder, original_yborder)
        img_2_put = cv2.copyMakeBorder(img_2_put,10,10,10,10,cv2.BORDER_CONSTANT,value=[0,0,0])

        x_offset = int(width - 80 - img_2_put.shape[1])
        y_offset = int(510 - img_2_put.shape[0] / 2)
        background = self.overlay_image(background, img_2_put, x_offset, y_offset)

        # put text
        movie_name = movie_name[0].upper() + movie_name[1:]
        text_to_show = "{}".format(movie_name)
        cv2_im_rgb = cv2.cvtColor(background,cv2.COLOR_BGR2RGB)
        pil_im = Image.fromarray(cv2_im_rgb)
        draw = ImageDraw.Draw(pil_im)
        font = ImageFont.truetype(path2font, 48)
        draw.text((84, 1695), text_to_show, font=font, fill=(237, 155, 0, 1))
        background = cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)

        cv2.imwrite(path2combined, background)
        return background.shape


    def to_blurface(self, path2combined, background='blurface'):
        '''Create blurface image & save in path2combined.

        param background:
            - blurface;
            - curcles.
        '''

        path2background = os.path.join('web_app/static/web_app/images/', 'background_{}_img.jpg'.format(background))
        path2hinzu = os.path.join('web_app/static/web_app/images/', 'hinzu.png')
        assert os.path.exists(path2background) and os.path.exists(path2hinzu), \
               'invalid background or hinzu`s logo paths.'

        background = cv2.imread(path2background)
        hinzu = cv2.imread(path2hinzu, -1)  # also read alpha chanel
        similar = cv2.imread(self.path2similar)
        original = cv2.imread(self.path2original)

        # put hinzu logo image
        x_offset = background.shape[1] - hinzu.shape[1] - 80
        y_offset = background.shape[0] - hinzu.shape[0] - 80
        background = self.overlay_image(background, hinzu, x_offset, y_offset)

        # resize images
        x, y = int(background.shape[1]/2.2 - 180), int(background.shape[0]/2.5)
        original = self.resize_image(original, x, y)
        # lets resize width of similar to the same as original
        similar = self.resize_image(similar, original.shape[1], y)

        # check if vertical
        # add then black background if not
        similar = self.overlay_on_black_vertical(image=similar, y=y, area=0.65)
        original = self.overlay_on_black_vertical(image=original, y=y)

        # rotate
        similar = cv2.cvtColor(similar, cv2.COLOR_BGR2BGRA)  # to RGBA
        similar = self.rotate_image(similar, -15)

        original = cv2.cvtColor(original, cv2.COLOR_BGR2BGRA)
        original = self.rotate_image(original, 15)

        # put original
        x_combined = original.shape[1] - original.shape[1] / 3 + similar.shape[1]
        x_offset = int((background.shape[1] - x_combined)/2)
        y_offset = int(background.shape[0]/3 - original.shape[0]/2)
        background = self.overlay_image(background, original, x_offset, y_offset)

        # put similar
        x_offset = int(x_offset + 2/3*original.shape[1])
        y_offset = int(y_offset + original.shape[0]/2)
        background = self.overlay_image(background, similar, x_offset, y_offset)

        cv2.imwrite(path2combined, background)
        return background.shape
