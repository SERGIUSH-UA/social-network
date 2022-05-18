from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import json
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import *


@ensure_csrf_cookie
def index(request):
    return render(request, "network/index.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required
def posts(request):
    # Composing a new post must be via POST
    if request.method != "POST" and request.method != "GET":
        return JsonResponse({"error": "POST request required."}, status=400)

    if request.method == "POST":
        # Check data
        if "body" in request.POST:
            body = request.POST["body"]
        else:
            return JsonResponse({"error": "Body request required."}, status=400)

        # Create one email for each recipient, plus sender
        post_p = Post(owner=request.user, body=body)
        post_p.save()
        user_p = User.objects.get(id=request.user.id)
        return JsonResponse(post_p.serialize(user=user_p, new=True), status=201)
    else:
        if "id" in request.GET:
            post_id = int(request.GET["id"])
            if post_id == -10:
                last_ten = Post.objects.all().order_by('-id')[:10]
            elif request.GET["eq"] == "lt":
                last_ten = Post.objects.filter(id__lt=post_id).order_by('-id')[:10]
            else:
                last_ten = Post.objects.filter(id__gt=post_id).order_by('-id')[:10]

            if len(last_ten) != 0:
                last_id = last_ten[len(last_ten)-1].id
            else:
                last_id = 0
            user_p = User.objects.get(id=request.user.id)
            return JsonResponse([post_p.serialize(user=user_p, new=False) for post_p in last_ten], safe=False, status=201,
                                headers={"last_id": last_id})
        else:
            return JsonResponse({"error": "Error GET."}, status=400)


@login_required
def post(request, post_id):
    # Query for requested post
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    # Return email contents
    if request.method == "GET":
        user_p = User.objects.get(id=request.user.id)
        return JsonResponse(post.serialize(new=False, user=user_p))

    # Update whether email is read or should be archived
    elif request.method == "PUT":
        post = Post.objects.get(owner=request.user, pk=post_id)
        data = json.loads(request.body)
        if data.get("body") is not None:
            post.body = data["body"]
        if data.get("archived") is not None:
            post.archived = data["archived"]
        post.save()
        return HttpResponse(status=204)

    # Email must be via GET or PUT
    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)


def user(request, user_id):
    # Query for requested post
    try:
        user_p = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)

    # Return email contents
    if request.method == "GET":
        return JsonResponse(user_p.serialize())

    # Update whether email is read or should be archived
    elif request.method == "PUT":
        data = json.loads(request.body)
        if data.get("name") is not None:
            user_p.name = data["name"]
        if data.get("birthday") is not None:
            user_p.birthday = data["birthday"]
        user_p.save()
        return HttpResponse(status=204)

    # Email must be via GET or PUT
    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)


def comments(request):
    # Composing a new comments must be via POST
    if request.method != "POST" and request.method != "GET":
        return JsonResponse({"error": "POST request required."}, status=400)

    if request.method == "POST":
        # Check data
        if "body" in request.POST:
            body = request.POST["body"]
            post_id = int(request.POST["post_id"])
        else:
            return JsonResponse({"error": "Body request required."}, status=400)

        # Create one email for each recipient, plus sender
        comment_p = Comment(owner=request.user, comment=body, post_id=post_id)
        comment_p.save()

        return JsonResponse(comment_p.serialize(), status=201)
    else:
        if "id" in request.GET:
            comment_id = int(request.GET["id"])
            post_id = int(request.GET["post_id"])
            if comment_id == -10:
                last_ten = Comment.objects.filter(post_id=post_id).order_by('-id')[:10]
            elif request.GET["eq"] == "lt":
                last_ten = Comment.objects.filter(id__lt=comment_id, post_id=post_id).order_by('-id')[:10]
            else:
                last_ten = Comment.objects.filter(id__gt=comment_id, post_id=post_id).order_by('-id')[:10]

            if len(last_ten) != 0:
                last_id = last_ten[len(last_ten)-1].id
            else:
                last_id = 0
            user_avatar = User.objects.get(id=request.user.id).user_avatar.url
            return JsonResponse([comment_p.serialize() for comment_p in last_ten], safe=False, status=201,
                                headers={"last_id": last_id})
        else:
            return JsonResponse({"error": "Error GET."}, status=400)


def likes(request):
    # Composing a new like must be via POST
    if request.method != "POST" and request.method != "GET":
        return JsonResponse({"error": "POST request required."}, status=400)

    if request.method == "POST":
        # Check data
        if "post_id" in request.POST:
            post_id = int(request.POST["post_id"])
        else:
            return JsonResponse({"error": "post_id request required."}, status=400)

        try:
            like_p = Like.objects.get(owner=request.user, post_id=post_id)
            like_p.delete()
        except Like.DoesNotExist:
            like_p = Like(owner=request.user, post_id=post_id)
            like_p.save()

        return HttpResponse(status=201)
    else:
        if "id" in request.GET:
            comment_id = int(request.GET["id"])
            post_id = int(request.GET["post_id"])
            if comment_id == -10:
                last_ten = Comment.objects.filter(post_id=post_id).order_by('-id')[:10]
            elif request.GET["eq"] == "lt":
                last_ten = Comment.objects.filter(id__lt=comment_id, post_id=post_id).order_by('-id')[:10]
            else:
                last_ten = Comment.objects.filter(id__gt=comment_id, post_id=post_id).order_by('-id')[:10]

            if len(last_ten) != 0:
                last_id = last_ten[len(last_ten)-1].id
            else:
                last_id = 0
            user_avatar = User.objects.get(id=request.user.id).user_avatar.url
            return JsonResponse([comment_p.serialize() for comment_p in last_ten], safe=False, status=201,
                                headers={"last_id": last_id})
        else:
            return JsonResponse({"error": "Error GET."}, status=400)