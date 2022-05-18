
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    # API Routes
    path("posts", views.posts, name="posts"),
    path("comments", views.comments, name="comments"),
    path("likes", views.likes, name="likes"),
    path("posts/<int:post_id>", views.post, name="post"),
    path("users/<int:user_id>", views.user, name="user"),

]
