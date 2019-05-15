import os
import numpy as np
import tensorflow as tf
from keras.models import load_model 
from keras.applications import VGG16
from keras.applications.vgg16 import preprocess_input, decode_predictions
from keras.preprocessing.image import load_img, img_to_array
from keras.models import load_model
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
graph = tf.get_default_graph()

def upload_file(request):

    predicted = False

    if request.method == 'POST':
        print('Debug upload if')
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            print('Debug upload if if')
            handle_uploaded_file(request.FILES['file'])
            #post = predict()
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
    post = None

    global graph
    with graph.as_default():
        model = VGG16()

        #img = load_img('blog/tmp/tmp_img', target_size=(224, 224))
        img = load_img(tmp_img, target_size=(224, 224))
        arr_data = img_to_array(img)
        arr_data = preprocess_input(arr_data)
        arr_input = np.stack([arr_data])

        # prediction
        probs = model.predict(arr_input)
        results = decode_predictions(probs)
        print(results[0])
        print('!#!# Debug End.')
        post = results[0]

        return post

