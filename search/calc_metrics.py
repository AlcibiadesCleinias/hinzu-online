import argparse

import numpy as np

import PIL
import tqdm
import os

import cv2

from bs4 import BeautifulSoup
import io
import requests
import time

from joblib import Parallel, delayed

import sys
sys.path.append('..')

from backend.ml import models
from backend.ml.hnsw_wrapper import Index

import cv2
import imutils
import pkg_resources

HAAR_XML = pkg_resources.resource_filename(
    'cv2', 'data/haarcascade_frontalface_default.xml')
FACE_CASCADE = cv2.CascadeClassifier(HAAR_XML)


def upload_model(args):
    if args.model_name == 'BeheadedDenseNet121':
        return models.BeheadedDenseNet121()
    if args.model_name == 'PretrainedHeadOnTLL3LayersV1DenseNet121':
        return models.PretrainedHeadOnTLLV1DenseNet121()
    assert False, 'Set bad model name {}'.format(args.model_name)


def count_face_automatically(file_path : str):
    image = cv2.imread(file_path)
    image = imutils.resize(image, width=512)
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    faces = FACE_CASCADE.detectMultiScale(gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(32, 32)
    )

    return len(faces)

def offline(args):
    model = upload_model(args).train(False)

    index = Index(space='cosine', dim=model.output_embeddings_shape())
    index.load_index(args.index_path)

    face_counters = {}

    for data in os.walk(args.test_img_dir):
        path, subdirs, files = data
        for f in tqdm.tqdm(files, position=0):
            if f.split('.')[-1].lower() not in ['jpg', 'jpeg', 'png']:
                continue

            file_path = os.path.join(path, f)
            n_face_orig = count_face_automatically(file_path)

            e = models.calc_embed(model, file_path)
            labels, distances = index.knn_query([e], k=1)
            file_in_base = os.path.join(args.base_img_dir, labels[0][0])

            n_face_find = count_face_automatically(file_in_base)
            face_counters[file_path] = (n_face_orig, n_face_find)

    counters = np.zeros((2,2))

    ones = 0

    for k in face_counters.keys():
        label = int(face_counters[k][0] > 1)
        prediction = int(face_counters[k][1] > 1)
        ones += label
        counters[label][prediction] += 1

    counters[1] /= ones
    counters[0] /= (len(face_counters) - ones)

    print('Number of images matched to the same number of persons: one or more (based on Haar classifier)')
    print('one: {}'.format(counters[0][0]))
    print('two or more: {}'.format(counters[1][1]))



def online(args):
    res = []
    times = []
    print('Test service responce time:')

    for data in os.walk(args.test_img_dir):
        path, subdirs, files = data
        for f in tqdm.tqdm(files, position=0):
            if f.split('.')[-1].lower() not in ['jpg', 'jpeg', 'png']:
                continue
            file_path = os.path.join(args.test_img_dir, f)
            start_counter = time.perf_counter()
            res.append([file_path, get_image_from_service(args.service_url, file_path)])
            times.append(time.perf_counter() - start_counter)

    times = np.array(times)
    print('mean: {:.2f} s, std: {:.2f}s'.format(np.mean(times), np.std(times)))
    arg_times = np.argsort(times)
    times = np.sort(times)
    N = len(times)
    q05, q50, q95 = int(N*0.05), int(N * 0.50), int(N*0.95)

    print('q05: {:.2f} s, example: {}'.format(times[q05], res[arg_times[q05]][0]))
    print('q50: {:.2f} s, example: {}'.format(times[q50], res[arg_times[q50]][0]))
    print('q95: {:.2f} s, example: {}'.format(times[q95], res[arg_times[q95]][0]))

    print('OK')

    print('Test highload: try request {} jobs in parallel'.format(args.n_jobs))

    def wrapper(p):
        return [p, get_image_from_service(args.service_url, p)]

    res = []

    start_counter = time.perf_counter()

    with Parallel(n_jobs=args.n_jobs) as parallel:
        res = parallel(delayed(wrapper)(os.path.join(args.test_img_dir, f)) \
            for f in tqdm.tqdm(os.listdir(args.test_img_dir), position=0) if f.split('.')[-1].lower() in ['jpg', 'jpeg', 'png'])

    print('Total time per image: {:.2f} s'.format((time.perf_counter() - start_counter) / len(times)))
    print('OK')


def get_image_from_service(url : str, path_to_file : str):
    files = {'file': open(path_to_file, 'rb')}
    r = requests.post(url + '/', files=files)
    soup = BeautifulSoup(r.text, 'html.parser')

    fetch_path = None
    for s in str(soup).split('"'):
        if 'api/fetch' in s:
            fetch_path = s
            break

    if fetch_path is None:
        assert False, "Bad service responce, see full answer: {}".format(r.content)

    r_fetch = requests.get(url + fetch_path)

    return io.BytesIO(r_fetch.content)


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers()
    offline_parser = subs.add_parser('offline', description='calc offline metrics based on images set and search index')
    online_parser = subs.add_parser('online', description='calc online metrics based on production instance')

    offline_parser.add_argument('--test-img-dir', type=str, required=True,
                    help='Directory with images dataset for metrics calculation.')
    offline_parser.add_argument('--base-img-dir', type=str, required=True,
                    help='Directory with images search base.')
    offline_parser.add_argument('--index-path', type=str, required=True,
                    help='Hnsw index (in zip format) which built on images search base(--img-base-dir param).')
    offline_parser.add_argument('--model-name', type=str, required=False, default='BeheadedDenseNet121',
                        help='Model name for image processing (must produce same embedding as stored in hnsw index).')

    online_parser.add_argument('--test-img-dir', type=str, required=True,
                    help='Directory with images dataset for metrics calculation.')
    online_parser.add_argument('--n-jobs', type=int, required=True,
                    help='Number of jobs for perf test.')
    online_parser.add_argument('--service-url', type=str, required=True,
                    help='Hinzu instance url address.')


    offline_parser.set_defaults(func=offline)
    online_parser.set_defaults(func=online)


    parsed = parser.parse_args()
    parsed.func(parsed)
