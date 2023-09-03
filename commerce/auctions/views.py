from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils.functional import lazy as _
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages

from .models import User, Auctions, Watchlist, Bids, Comment
from .forms import CreateListing, CommentForm
from .utils import MainCategories


def index(request):
    listings = Auctions.objects.filter(open=True).order_by("-pk")
    return render(request, "auctions/index.html", {
        "listings": listings
    })

def all_view(request):
    listings = Auctions.objects.all().order_by("-pk")
    return render(request, "auctions/all.html", {
        "listings": listings
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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")

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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required(login_url="login")
def create_listing(request):
    if request.method == "POST":
        form = CreateListing(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            category = form.cleaned_data['category']
            bid = form.cleaned_data["bid"]
            image_url = form.cleaned_data["image_url"]
            description = form.cleaned_data["description"]
            if not image_url:
                auction = Auctions.objects.create(user=request.user, title=title, category=category, bid=bid, description=description)
                auction.save()
            else:
                auction = Auctions.objects.create(user=request.user, title=title, category=category, bid=bid, image_url=image_url, description=description)
                auction.save()
            
        return HttpResponseRedirect(reverse("index"))
    
    else:
        return render(request, "auctions/create.html", {
            "form": CreateListing()
        })

def listing_view(request, id):

    try:
        listing = Auctions.objects.get(pk=id)
        bid = Bids.objects.filter(listing=listing)
        comments = Comment.objects.filter(listing=listing)

    except:
        raise Http404("Invalid Listing")
    
    in_watchlist = False
    if request.user.is_authenticated:
        watchlist = Watchlist.objects.filter(user=request.user, listing=id)
        if watchlist.exists():
            in_watchlist = True


    if request.method == "POST":
        form = CommentForm(request.POST)
        if not form.is_valid():
            return HttpResponseRedirect(reverse("listing_view",kwargs={"id":id}))
        
        comment = form.cleaned_data['comment']
        try:
            comment_add = Comment.objects.create(user=request.user, listing=listing, comment=comment)
            comment_add.save()
        except:
            return HttpResponseRedirect(reverse("listing_view",kwargs={"id":id}))
            
        return HttpResponseRedirect(reverse("listing_view",kwargs={"id":id}))
        
    else:
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "bid_count": bid.count(),
            "winner": bid.last(),
            "commentForm": CommentForm(),
            "comments": comments.order_by("-date")[:15],
            "watchlist":in_watchlist
        })

@login_required(login_url="login")
def watchlist_view(request):

    watchlist =  Watchlist.objects.filter(user_id=request.user.id)
    listing = Auctions.objects.filter(pk__in=watchlist.values_list("listing")).order_by("-pk")
    # return HttpResponse(listing)
    
    return render(request, "auctions/watchlist.html",{
        "listings": listing
    })

@login_required(login_url="login")
def watchlist_add(request, id):
    if request.method == "POST":
        if not Watchlist.objects.filter(user=request.user, listing_id = id):
            listing = Auctions.objects.get(pk=id)
            # return HttpResponse(f"{listing.bid}")
            watchlist = Watchlist.objects.create(user=request.user, listing=listing)
            watchlist.save()
        else:
            watchlist = Watchlist.objects.get(user=request.user, listing_id=id)
            watchlist.delete()
    
        return HttpResponseRedirect(reverse("watchlist"))
    else:
        return HttpResponseRedirect(reverse("watchlist"))

@login_required(login_url="login")
def listing_close(request, id):
    if request.method == "POST":
        listing = Auctions.objects.get(user=request.user, pk=id)
        listing.open = False
        listing.save()
        return HttpResponseRedirect(reverse("listing_view",kwargs={"id":id}))
    else:
        return HttpResponseRedirect(reverse("index"))

@login_required(login_url="login")

def bid(request, id):
    if request.method == "POST":

        if not request.POST['bid']:
            messages.error(request, "Please input a bid")
            return HttpResponseRedirect(reverse("listing_view",kwargs={"id":id}))
        
        try:
            bid = float(request.POST["bid"])
        except:
            messages.error(request, "Please Input a number!")
            return HttpResponseRedirect(reverse("listing_view",kwargs={"id":id}))

        listing = Auctions.objects.get(pk=id)


        if bid <= listing.bid:
            messages.error(request, "Your bid should be higher than the current bid!")
            return HttpResponseRedirect(reverse("listing_view",kwargs={"id":id}))
        
        try:
            addbid = Bids.objects.create(user=request.user, listing=listing, old_bid=listing.bid, current_bid=bid)
            addbid.save()
            listing.bid = bid
            listing.save()
        except:
            return HttpResponseRedirect(reverse("listing_view",kwargs={"id":id}))
            

        return HttpResponseRedirect(reverse("listing_view",kwargs={"id":id}))
    else:
        return HttpResponseRedirect(reverse("index"))

def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": MainCategories
    })

def category(request, category="All"):
    if category == "All":
        listings = Auctions.objects.filter(open=True).order_by("-pk")
        return render(request, "auctions/category.html", {
            "listings": listings,
            "category": category
        })
    
    
    if category not in MainCategories:
        raise Http404("Invalid Page")
    
    listings = Auctions.objects.filter(category=category, open=True).order_by("-pk")
    return render(request, "auctions/category.html", {
        "listings": listings,
        "category": category
    })

def user_view(request, username):
    try:
        user = User.objects.get(username=username)
        listing = Auctions.objects.filter(user=user)

    except:
        raise Http404("Url Does Not Exist!")

    return render(request, "auctions/user.html", {
        "username": username,
        "listings":listing

    })

