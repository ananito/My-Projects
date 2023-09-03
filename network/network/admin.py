from django.contrib import admin

# Register your models here.
from .models import User, Post, Following

admin.site.register(User)
admin.site.register(Post)
admin.site.register(Following)
