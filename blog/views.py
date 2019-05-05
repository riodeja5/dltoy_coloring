import os
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
#from .forms import UploadForm
from .forms import UploadFileForm

# Imaginary function to handle an uploaded file.
# from somewhere import handle_uploaded_file

graph = tf.get_default_graph()

def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})

def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    return render(request, 'blog/post_list.html', {'posts': posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})

def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})

def dltoy(request):
    if request.method == "POST":
        # TOOD proc dl
        post = "at if"
        print('!#!# Debug Start.')
        model = VGG16()
        img_dog = load_img('img/dog.jpg', target_size=(224, 224))
        img_cat = load_img('img/cat.jpg', target_size=(224, 224))
        arr_dog = img_to_array(img_dog)
        arr_cat = img_to_array(img_cat)
        arr_dog = preprocess_input(arr_dog)
        arr_cat = preprocess_input(arr_cat)
        arr_input = np.stack([arr_dog, arr_cat])

        # prediction
        probs = model.predict(arr_input)
        results = decode_predictions(probs)
        print(results[0])
        print('!#!# Debug End.')
        post = results[0]
    else:
        #posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
        post = "at else"
    return render(request, 'blog/dltoy.html', {'post': post})

def upload_file(request):
    if request.method == 'POST':
        print('Debug upload if')
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            print('Debug upload if if')
            handle_uploaded_file(request.FILES['file'])
            post = predict()

    else:
        print('Debug upload else')
        post = 'else'
        form = UploadFileForm()
    return render(request, 'blog/upload.html', {'form': form, 'post': post})

def handle_uploaded_file(f):
    with open('blog/tmp/tmp_img', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def predict():
    post = None

    global graph
    with graph.as_default():
        model = VGG16()
        img = load_img('blog/tmp/tmp_img', target_size=(224, 224))
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

"""
class Upload(generic.FormView):
    form_class = UploadForm
    template_name = 'blog/upload.html'

    def form_valid(self, form):
        download_url = form.save()
        context = {
            'download_url': download_url,
            'form': form,
        }
        return self.render_to_response(context)
"""

