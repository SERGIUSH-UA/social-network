import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    user_avatar = models.ImageField(blank=True, default="no-avatar-png-transparent.png")
    following = models.ManyToManyField('self', related_name="followers", blank=True, symmetrical=False)
    birthday = models.DateField(blank=True, verbose_name="Birthday")
    work_place = models.CharField(blank=True, verbose_name="Work place", max_length=90)
    native_city = models.CharField(max_length=80, verbose_name="City", default="")
    native_country = models.CharField(max_length=80, verbose_name="Country", default="")


class Post(models.Model):
    date_create = models.DateTimeField(blank=True, auto_now_add=True, verbose_name="Created date")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    body = models.CharField(max_length=512)

    def __str__(self):
        return f"{self.id} Post:  {self.date_create} by {self.owner}"

    def serialize(self, new, user):
        return {
            "id": self.id,
            "owner": self.owner.id,
            "ownerName": self.owner.username,
            "timestamp": self.date_create.strftime("%b %d %Y, %I:%M %p"),
            "time": self.date_create.strftime("%H:%M"),
            "date": get_ty_day(self.date_create),
            "body": self.body,
            "likes": self.likes.count(),
            "avatar": self.owner.user_avatar.url,
            "comment_avatar": user.user_avatar.url,
            "comments": self.comments.count(),
            "truncate": True,
            "new": new,
            "liked": if_liked_post(user, self)
        }

    def simpl_serialize(self):
        return {
            "id": self.id,
            "owner": self.owner.id,
            "ownerName": self.owner.username,
            "timestamp": self.date_create.strftime("%b %d %Y, %I:%M %p"),
            "time": self.date_create.strftime("%H:%M"),
            "date": get_ty_day(self.date_create),
            "body": self.body,
            "likes": self.likes.count(),
            "avatar": self.owner.user_avatar.url,
            "comments": self.comments.count()
        }


def get_ty_day(date):
    today = timezone.now()
    yesterday = today - datetime.timedelta(days=1)
    if date.strftime("%b %d %Y") == today.strftime("%b %d %Y"):
        return 'today'
    elif date.strftime("%b %d %Y") == yesterday.strftime("%b %d %Y"):
        return 'yesterday'
    else:
        return date.strftime("%b %d %Y")

def if_liked_post(user, post):
    try:
        like = Like.objects.get(owner=user, post=post)
    except Like.DoesNotExist:
        return False
    return True


class Like(models.Model):
    date_create = models.DateTimeField(default=timezone.now, name="Created date")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")

    def __str__(self):
        return f"Like: {self.date_create} by {self.owner}"


class Comment(models.Model):
    date_created = models.DateTimeField(verbose_name="Created date", default=timezone.now)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    comment = models.CharField(max_length=512)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")

    def __str__(self):
        return f"Comment: {self.date_created} by {self.owner} for {self.post}"

    def serialize(self):
        return {
            "id": self.id,
            "owner": self.owner.id,
            "ownerName": self.owner.username,
            "timestamp": self.date_created.strftime("%b %d %Y, %I:%M %p"),
            "time": self.date_created.strftime("%H:%M"),
            "date": get_ty_day(self.date_created),
            "body": self.comment,
            "avatar": self.owner.user_avatar.url
        }


