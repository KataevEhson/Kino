import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from .models import *





def registration(request):
    error = ''
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if username and email and password:
            try:
                User.objects.create_user(username=username, email=email, password=password)
            except IntegrityError:
                error = 'Ин номи корбар аллакай истифода мешавад.'
            else:
                return redirect('login')
        else:
            error = 'Ҳамаи майдонҳоро пур кунед.'
    return render(request, 'registration.html', {'error': error})


def login_user(request):
    error = ''
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        error = 'Номи корбар ё рамз нодуруст аст.'
    return render(request, 'login.html', {'error': error})


@login_required
def create_video(request):
    if request.method == 'POST':
        Video.objects.create(
            user_id=request.user,
            title=request.POST['title'],
            author=request.POST['author'],
            caption=request.POST['caption'],
            category_id=Ganr.objects.get(pk=request.POST['category']),
            video=request.FILES['video'],
            image=request.FILES['image'],
        )
        return redirect('create_video')
    categories = Ganr.objects.all()
    return render(request, 'create_video.html', {'categories': categories})







def show_video(request):
    videos = Video.objects.all()
    categories = Ganr.objects.all()
    return render(request, 'home.html', {'videos': videos,'categories': categories,})





def category_video(request, pk):
    videos = Video.objects.filter(category_id=pk)
    categories = Ganr.objects.all()
    return render(request, 'home.html', {
        'videos': videos,
        'categories': categories,
        'selected_category': pk,
    })





def video_keywords(video):
    text = f'{video.title} {video.caption}'.casefold()
    return {word for word in re.findall(r'[^\W\d_]+', text) if len(word) >= 3}


def related_videos(video):
    keywords = video_keywords(video)
    recommendations = []
    candidates = Video.objects.exclude(pk=video.pk).only(
        'title', 'caption', 'category_id', 'created_at',
    )

    for candidate in candidates:
        candidate_keywords = video_keywords(candidate)
        shared_words = keywords & candidate_keywords
        same_category = candidate.category_id_id == video.category_id_id
        if same_category or shared_words:
            similarity = len(shared_words) / max(len(keywords | candidate_keywords), 1)
            score = similarity + 0.25 * same_category
            recommendations.append((score, candidate))

    recommendations.sort(
        key=lambda item: (item[0], item[1].created_at, item[1].pk),
        reverse=True,
    )
    return [candidate for _, candidate in recommendations[:4]]


def watch_video(request, pk):
    video = get_object_or_404(Video, pk=pk)
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
        text = request.POST.get('text')

        Comment.objects.create(
            user_id=request.user,
            author=request.user.username,
            text=text,
            video=video,
        )
        return redirect('video_comments', pk=pk)
    return render(request, 'watch.html', {
        'video': video,
        'recommendations': related_videos(video),
    })


def video_comments(request, pk):
    video = get_object_or_404(Video, pk=pk)
    comments = Comment.objects.filter(video=video)
    return render(request, 'comments.html', {'video': video, 'comments': comments})



