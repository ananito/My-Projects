import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger



from django.urls import reverse
from django.contrib import messages

from .models import User, Post, Following


def index(request):
    posts_list = Post.objects.all().order_by("-pk")

    paginator = Paginator(posts_list, 10)

    page = request.GET.get("page", 1)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
            
    
    

    return render(request, "network/index.html", {
        "posts":posts,
    })


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

@login_required(login_url="login")
def newpost(request):
    if request.method == "POST":

        # Get the post data
        text = request.POST["newPost"]
        user = request.user

        if not text:
            return HttpResponseRedirect(reverse("index"))
        
        if text.isspace():
            return HttpResponseRedirect(reverse("index"))
        
        
        post = Post.objects.create(user=user, text=text)
        post.save()

        return HttpResponseRedirect(reverse("index"))
    else:
        return HttpResponseRedirect(reverse("index"))

def profile(request, username):

    # Make sure that the request is only a get request
    if request.method != "GET":
        return HttpResponseRedirect(reverse("index"))

    # Try to see if the username exists
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return HttpResponseNotFound(f"{username} is not found. Are you sure {username} is spelt correctly.")

    try:
        followers = Following.objects.filter(user=user)
        following = Following.objects.filter(follower=user)
        posts_list = Post.objects.filter(user=user).order_by("-pk")
        
    except:
        pass

    # Check if the user is the same user who made the request
    if request.user == user:
        follow = False
    elif request.user != user:
        follow = True

    followed = False
    if request.user.is_authenticated:
        try:
            followed = Following.objects.get(follower=request.user, user=user)
        except:
            followed = False

    paginator = Paginator(posts_list, 10)

    page = request.GET.get("page", 1)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, "network/profile.html", {
        "username": user,
        "follow": follow,
        "followers": followers.count(),
        "following": following.count(),
        "postsCount": posts_list.count(),
        "posts": posts,
        "followed": followed
    })

@csrf_exempt
@login_required(login_url="login")
def follow(request):

    # Follow or unfollow must be a POST request
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=400)
        
    data = json.loads(request.body)
    

    
    # Validate the user exist before progressing
    try:
        if data.get("user") is not None:
            user = User.objects.get(username=data.get("user"))
        
        # If the user edited the html to submit something else
        if data.get("user") is None:
            return JsonResponse({"error": "Invaild User!"}, status=400)
    except:
        return JsonResponse({"error": "User does not exits."}, status=400)

    # Try to see if the two users are the same
    if user == request.user:
        return JsonResponse({"error": "The user can not follow themself!"}, status=400)


    # Check if the user already followed the other user
    try:
        # if the user exists then we have to unfollow
        follow = Following.objects.get(user=user, follower=request.user)
        if follow:
            follow.delete()
    except Following.DoesNotExist:
        # if the user does not exist
        follow = Following.objects.create(user=user, follower=request.user)
        follow.save()
        return JsonResponse({"success": f"The user {user} was followed by {request.user}"}, status=201)
        
    return JsonResponse({"success": f"The user {user} was unfollowed by {request.user}"}, status=201)


@login_required(login_url="login")
def follow_view(request):
    if request.method != "GET":
        return HttpResponseRedirect(reverse("index"))

    # First get a list of people following the user
    try:
        followers = Following.objects.filter(follower=request.user).values("user")
    except:
        return HttpResponse("The user does not follow anyone!")
    
    try:
        posts_list = Post.objects.filter(user__in=followers).order_by("-pk")
    except:
        return HttpResponse("No Posts!")

    paginator = Paginator(posts_list, 10)

    page = request.GET.get("page", 1)

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
        

    
    return render(request, "network/followings.html", {
        "posts":posts
    })

@csrf_exempt
@login_required(login_url="login")
def postUpdate(request):


    # Make sure that only a PUT request is accepted
    if request.method != "PUT":
        return JsonResponse({"error": "PUT Request Required"}, status=400)

    data = json.loads(request.body)

    # See if the post exist and if the user is the author
    try:
        post = Post.objects.get(id=data.get("postId"), user=request.user)
    except:
        return JsonResponse({"error": "Invalid User or Post Id"}, status=409)

    try:
        post.text = data.get("postBody")
        post.save()
    except:
        JsonResponse({"error": "Unable to save data!"}, status=400)
    return JsonResponse({"success": f"update successful"}, status=200)

@csrf_exempt
@login_required(login_url="login")
def like(request):
    if request.method != "PUT":
        return JsonResponse({"error": "PUT Request Required!"}, status=400)
    data = json.loads(request.body)

    # See if the post exist
    try:
        post = Post.objects.get(id=data.get("postId"))
        user = User.objects.get(id=request.user.id)
    except:
        return JsonResponse({"error": "Invalid Post"}, status=409)
    
    
    # See if User Already Like The Post
    try:
        if post.user_likes.get(username=user.username):
            post.user_likes.remove(user)
            post.likes = post.likes -1
            post.save()

    except User.DoesNotExist:
        post.user_likes.add(user)
        post.likes = post.likes + 1
        post.save()
        
    return JsonResponse({"likes": f"{post.likes}"}, status=200)
