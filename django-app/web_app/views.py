from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, FileResponse, HttpResponse, Http404
from django.urls import reverse
import json
from django.conf import settings
from .models import Rate, Embed
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.http import require_POST

from werkzeug.utils import secure_filename
from .script import find_similar, preprocess, ImageTemplate
import os
import sys
from cryptography.fernet import Fernet
from PIL import Image, ExifTags
import cv2
from random import randint
from .ml.models import fix_PIL_img_shape
import time

from subprocess import Popen
import logging

from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# set up logging
# logger = logging.getLogger('gunicorn.error')
# logger.handlers.extend(gunicorn_error_logger.handlers)
# logger.setLevel(logging.DEBUG)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[-1].lower() in ALLOWED_EXTENSIONS

def save_orientationed_image(file, filepath):
    image=Image.open(file)
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation]=='Orientation':
                break
        exif=dict(image._getexif().items())

        if exif[orientation] == 3:
            image=image.rotate(180, expand=True)
        elif exif[orientation] == 6:
            image=image.rotate(270, expand=True)
        elif exif[orientation] == 8:
            image=image.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        if image.mode != 'RGB':
            image = fix_PIL_img_shape(image)
    finally:
        image.save(filepath)
        image.close()

def how2put_image_into_html(image_shape):
    yborder, xborder = 550, 300  # numbers from html accordingly
    kx = image_shape[1]/xborder
    if yborder >= image_shape[0]/kx:
        # expand with x (width)
        return 'width_mode'
    else:
        # expand with y (height)
        return 'heigh_mode'

def get_movie_name(path2img):
    path2img = path2img.split('/')
    path2img = path2img[-1].split('$')
    if len(path2img) == 1:
        print('Waring: {} is not a name for movie'.format(path2img[0]))
        return None
    return path2img[0].split('-')

def vconcat_resize_min(images:list, interpolation=cv2.INTER_CUBIC):  # this func is deprecated
    w_min = min(im.shape[1] for im in images)
    im_list_resize = [cv2.resize(im, (w_min, int(im.shape[0] * w_min / im.shape[1])), interpolation=interpolation)
                      for im in images]
    return cv2.vconcat(im_list_resize)

# def fetch_user_ip():
    # if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
    #     app.logger.info('The main page was requested from ip : %s', request.environ['REMOTE_ADDR'])
    # else:
    #     app.logger.info('The main page was requested from ip %s', request.environ['HTTP_X_FORWARDED_FOR'])

def secure_filename_with_fix(filename):
    # https://stackoverflow.com/questions/21271465/saving-file-with-japanese-characters-in-python-3
    filename = secure_filename(filename)
    if '.' in filename:
        return filename
    return 'was_no_ascii_{}.'.format(randint(0, 100)) + filename

def dir_last_updated(folder):
    '''Trick for browser cache under static files'''
    path = os.path.join(settings.BASE_DIR, folder)
    return str(max(os.path.getmtime(os.path.join(root_path, f))
                   for root_path, dirs, files in os.walk(path)
                   for f in files))

################
# actual views #
################

class UploadImgView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        print(request.COOKIES)

        if len(request.session.items()) != 0:
            request.session.flush()

        try:
            file = request.FILES['file']
        except MultiValueDictKeyError:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

        if file and allowed_file(file.name):
            filename = secure_filename_with_fix(file.name)
            filename = str(randint(0, 1e+18)) + '_' + filename  # secure filename more
            path2original = os.path.join(settings.UPLOAD_FOLDER, filename)
            save_orientationed_image(file, path2original)
            domain = request.POST.get('magic_mode') or 'movies'
            domain = domain.split(' ')[-1]
            path2similar, embeds = find_similar(settings, path2original, domain=domain)

            # save to model
            embed_model = Embed(path2similar=path2similar,
                                embeds_of_original=embeds)
            embed_model.save()

            # we found similar so lets cancate imgs via template
            # default template
            domain = 'movies'
            # create super name for new image
            filename_combined = '{domain}_ts_{time}_{randomNoriginal}'.format(domain=domain,
                                                                              time=time.strftime('%d.%m.%Y.%H.%M.%S'),
                                                                              randomNoriginal=path2original.split('/')[-1])
            path2combined = os.path.join(settings.REPORTS_FOLDER, filename_combined)

            # create new image
            try:
                img_template = ImageTemplate(path2original, path2similar)
            except NameError:
                logger.error('Exception with ImageTemplate, user is redirected to upload page.')
                return HttpResponseRedirect(reverse('web_app:upload_file'))
            if domain == 'movies':
                shape_4_html = img_template.to_movie(path2combined,
                                                    ' '.join(get_movie_name(path2similar)))
            elif domain == 'blurface':
                shape_4_html = img_template.to_blurface(path2combined)
            else:
                shape_4_html = img_template.to_vertical_concated(path2combined)

            request.session['path2combined'] = path2combined

            # crypt url
            f = Fernet(settings.FERNET_KEY)
            path2combined_crypted = f.encrypt(path2combined.encode())

            # delete original image & pop cookie
            p = Popen("rm %s" % path2original, shell=True)
            # request.session.pop('path2original')
            rate_model = Rate(embeds=get_object_or_404(Embed, pk=embed_model.id),#pk=request.session.get('id')),
                              path2combined=path2combined,
                              pub_date=timezone.now())
            rate_model.save()
            request.session['rate_id'] = rate_model.id
            # in above it was like in prev. version
            ########

            # ... in api cookie seems like no needed
            # btw may be we should use it for show result only once!?
            request.session['id'] = embed_model.id
            request.session['path2similar'] = path2similar
            request.session['path2original'] = path2original
            # return HttpResponseRedirect(reverse('web_app:show_result', args=(domain,)))
            variables_dict = {
                            'id' : embed_model.id,
                            'message': "Фото успешно загружено. Hinzu подобрал фильм!",
                            'domain' : domain,
                            'path2combined_crypted' : path2combined_crypted.decode(),
                            }
            if domain == 'movies':
                variables_dict['movie_name'] = ' '.join(get_movie_name(path2similar)).capitalize()
                variables_dict['movie_name_4search'] = '+'.join(get_movie_name(path2similar))
            return Response(
                variables_dict,
                status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)


class RateImgView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request, *args, **kwargs):
        rate = request.POST.get('rate', None)
        if rate:
            message = 'Hinzu учтен Ваши пожелания!'
            rate_model = get_object_or_404(Rate, id=request.session.get('rate_id'))
            try:
                rate_model.rate = int(rate)
            except ValueError:
                rate_model.rate = None
            rate_model.save()
            variables_dict = {'message': message, 'rate':rate}
            return HttpResponse(json.dumps(variables_dict), content_type='application/json')
        return Response(status=status.HTTP_406_NOT_ACCEPTABLE)


def fetchImage(request, image_path_crypted):
    f = Fernet(settings.FERNET_KEY)
    try:
        image_path = f.decrypt(image_path_crypted.encode()).decode()
    except:
        raise Http404("Probably it is invalid file request!")
    try:
        response = FileResponse(open(image_path, 'rb'), as_attachment=False)
        return response
    except:
        raise Http404('file {} didnt find on server!'.format(image_path))

#########################
# hinzu on django views #
#########################

def upload_file(request):
    # fetch_user_ip()
    variables_dict = {'last_updated': dir_last_updated('web_app/static')}
    if len(request.session.items()) != 0:
        request.session.flush()
    if request.method == 'POST':
        file = request.FILES['file']
        if file and allowed_file(file.name):
            filename = secure_filename_with_fix(file.name)
            filename = str(randint(0, 1e+18)) + '_' + filename  # secure filename more
            path2original = os.path.join(settings.UPLOAD_FOLDER, filename)
            save_orientationed_image(file, path2original)
            domain = request.POST.get('magic_mode') or 'movies'
            domain = domain.split(' ')[-1]
            path2similar, embeds = find_similar(settings, path2original, domain=domain)

            # save to model
            embed_model = Embed(path2similar=path2similar,
                                embeds_of_original=embeds)
            embed_model.save()
            request.session['id'] = embed_model.id

            request.session['kinda_index_for_db'] = path2original
            request.session['path2similar'] = path2similar
            request.session['path2original'] = path2original
            return HttpResponseRedirect(reverse('web_app:show_result', args=(domain,)))
        else:
            return render(request, 'web_app/upload.html', variables_dict)
    else:
        return render(request, 'web_app/upload.html', variables_dict)


def show_result(request, domain):
    if request.session.get('path2original'):
        path2original = request.session.get('path2original')
        path2similar = request.session.get('path2similar')

        # create super name for new image
        filename_combined = '{domain}_ts_{time}_{randomNoriginal}'.format(domain=domain,
                                                                          time=time.strftime('%d.%m.%Y.%H.%M.%S'),
                                                                          randomNoriginal=path2original.split('/')[-1])
        path2combined = os.path.join(settings.REPORTS_FOLDER, filename_combined)

        # create new image
        try:
            img_template = ImageTemplate(path2original, path2similar)
        except NameError:
            logger.error('Exception with ImageTemplate, user is redirected to upload page.')
            return HttpResponseRedirect(reverse('web_app:upload_file'))
        if domain == 'movies':
            shape_4_html = img_template.to_movie(path2combined,
                                                ' '.join(get_movie_name(path2similar)))
        else:
            shape_4_html = img_template.to_vertical_concated(path2combined)

        request.session['path2combined'] = path2combined

        # crypt url
        f = Fernet(settings.FERNET_KEY)
        path2combined_crypted = f.encrypt(path2combined.encode())

        # render template
        variables_dict = {'last_updated': dir_last_updated('web_app/static'),
                          'domain' : domain,
                          'path2combined_crypted' : path2combined_crypted.decode(),
                          'image_mode' : how2put_image_into_html(shape_4_html),
                         }
        if domain == 'movies':
            variables_dict['movie_name'] = ' '.join(get_movie_name(path2similar))
            variables_dict['movie_name_4search'] = '+'.join(get_movie_name(path2similar))

        try:
            return render(request, 'web_app/result.html', variables_dict)
        except Exception as e:
            logger.error('Something went wrong in show_result! Error: {e}'.format(e))
            return HttpResponseRedirect(reverse('web_app:upload_file'))
        finally:
            # delete original image & pop cookie
            p = Popen("rm %s" % request.session.get('path2original'), shell=True)
            request.session.pop('path2original')
            rate_model = Rate(embeds=get_object_or_404(Embed, pk=request.session.get('id')),
                              path2combined=path2combined,
                              pub_date=timezone.now())
            rate_model.save()
            request.session['rate_id'] = rate_model.id
    else:
        return HttpResponseRedirect(reverse('web_app:upload_file'))


@require_POST
def addlike(request):
    if request.method == 'POST':
        rate = request.POST.get('rate', None)
        if rate:
            message = 'You liked this'
            rate_model = get_object_or_404(Rate, id=request.session.get('rate_id'))
            rate_model.rate = int(rate)
            rate_model.save()
    variables_dict = {'message': message}
    return HttpResponse(json.dumps(variables_dict), content_type='application/json')


def handler404(request, exception, template_name="web_app/404.html"):
    return render(request, template_name, status=404)


def favicon(request):
    image_path = 'web_app/static/web_app/images/favicon.ico'
    response = FileResponse(open(image_path, 'rb'), as_attachment=False)
    return response
