from django.contrib.auth.views import LogoutView
from django.urls import path, reverse_lazy
from .views import *

urlpatterns = [
    path("", registration, name="registration"),
    path("login/", login_user, name="login"),
    path("logout/", LogoutView.as_view(next_page=reverse_lazy("home")), name="logout"),
    path('create_video', create_video, name="create_video"),
    path('home', show_video, name='home'),
    path('category/<int:pk>/', category_video, name='category_video'),
    path('watch/<int:pk>/', watch_video, name='watch_video'),
    path('watch/<int:pk>/comments/', video_comments, name='video_comments'),
]
