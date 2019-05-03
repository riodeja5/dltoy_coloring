import numpy as np
from keras.applications import VGG16
from keras.applications.vgg16 import preprocess_input, decode_predictions
from keras.preprocessing.image import load_img, img_to_array
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Post
from .forms import PostForm

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

