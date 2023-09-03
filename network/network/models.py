from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(blank=False, null=False)
    likes = models.IntegerField(default=0, null=False)
    date = models.DateTimeField(auto_now_add=True)
    user_likes = models.ManyToManyField(User, related_name="user_likes", blank=True)
    
    def __str__(self):
        return f"{self.pk}"

class Following(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"The user {self.follower} follows {self.user}"