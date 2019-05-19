import os
import glob
import math
import cv2
import numpy as np
import tensorflow as tf
from keras.models import load_model 
from keras.applications import VGG16
from keras.applications.vgg16 import preprocess_input, decode_predictions
from keras.preprocessing.image import load_img, img_to_array
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views import generic
from django.http import HttpResponseRedirect
from .models import Post
from .forms import PostForm
from .forms import UploadFileForm

# Imaginary function to handle an uploaded file.
# from somewhere import handle_uploaded_file

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
tmp_img = os.path.join(THIS_FOLDER, 'tmp/tmp_img')
img_size = 224
graph = tf.get_default_graph()

def upload_file(request):

    predicted = False

    if request.method == 'POST':
        print('Debug upload if')
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            print('Debug upload if if')
            handle_uploaded_file(request.FILES['file'])
            post = predict()
            post = None
            predicted = True

    else:
        print('Debug upload else')
        post = ''
        form = UploadFileForm()
    return render(request, 'blog/upload.html', {
        'form': form,
        'post': post,
        'predicted': predicted,
    })

def handle_uploaded_file(f):
    # with open('blog/tmp/tmp_img', 'wb+') as destination:
    with open(tmp_img, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def predict():
    batch_size = 30
    post = None

    global graph
    with graph.as_default():
        autoencoder = load_model('blog/static/autoencoder.h5')

        input_lists = glob.glob(tmp_img)
        input_lab = get_lab_from_data_list(input_lists)
        input_steps = math.ceil(len(input_lists)/batch_size)
        input_gen = generator_with_preprocessing(input_lists, batch_size)

        input_pred = autoencoder.predict_generator(input_gen, steps=input_steps, verbose=0)

        x_input = []
        y_input = []
        for i, (l, ab) in enumerate(generator_with_preprocessing(input_lists, batch_size)):
            x_input.append(l)
            y_input.append(ab)
            if i == (input_steps - 1):
                break
        x_input = np.vstack(x_input)
        y_input = np.vstack(y_input)

        # LAB->RGB
        input_preds_lab = np.concatenate((x_input, input_pred), 3).astype(np.uint8)

        input_preds_rgb = []
        for i in range(input_preds_lab.shape[0]):
            preds_rgb = lab2rgb(input_preds_lab[i, :, :, :])
            input_preds_rgb.append(preds_rgb)
        input_preds_rgb = np.stack(input_preds_rgb)

        # save result
        cv2.imwrite('media/images/output.jpg', input_preds_rgb[0])

        return post

def rgb2lab(rgb):
    assert rgb.dtype == 'uint8'
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)

def lab2rgb(lab):
    assert lab.dtype == 'uint8'
    return cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)

def get_lab_from_data_list(data_list):
    x_lab = []
    for f in data_list:
        rgb = img_to_array(
            load_img(
                f,
                target_size=(img_size, img_size)
            )
        ).astype(np.uint8)
        lab = rgb2lab(rgb)
        x_lab.append(lab)
    return np.stack(x_lab)

def generator_with_preprocessing(data_list, batch_size, shuffle=False):
    while True:
       if shuffle:
           np.random.shuffle(data_list)
       for i in range(0, len(data_list), batch_size):
           batch_list = data_list[i:i + batch_size]
           batch_lab = get_lab_from_data_list(batch_list)
           batch_l = batch_lab[:, :, :, 0:1]
           batch_ab = batch_lab[:, :, :, 1:]
           yield(batch_l, batch_ab)


