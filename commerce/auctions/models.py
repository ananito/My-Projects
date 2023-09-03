from django.contrib.auth.models import AbstractUser
from django.db import models
from .utils import CATEGORIES



class User(AbstractUser):
    pass

class Auctions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=64, choices=CATEGORIES)
    bid = models.DecimalField(max_digits=9, decimal_places=2)
    image_url = models.URLField(default="https://placehold.co/160x240.png",null=False)
    description = models.TextField()
    open = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pk}:{self.title} - {self.user} bid: {self.bid} open = {self.open}"


class Bids(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Auctions, on_delete=models.CASCADE)
    old_bid = models.DecimalField(max_digits=9, decimal_places=2)
    current_bid = models.DecimalField(max_digits=9, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing =  models.ForeignKey(Auctions, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Auctions, on_delete=models.CASCADE)
    comment = models.TextField(null=True)
    date = models.DateTimeField(auto_now_add=True)
