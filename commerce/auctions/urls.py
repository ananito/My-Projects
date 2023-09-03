from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listing, name="create_listing"),
    path("listing/<int:id>", views.listing_view, name="listing_view"),
    path("all/", views.all_view, name="all_view"),
    path("listing/<int:id>/close", views.listing_close, name="listing_close"),
    path("watchlist/", views.watchlist_view, name="watchlist"),
    path("watchlist/<int:id>", views.watchlist_add, name="watchlist_add"),
    path("bid/<int:id>", views.bid, name="bid"),
    path("categories", views.categories, name="categories"),
    path("category/", views.category, name="category"),
    path("category/<str:category>", views.category, name="category"),
    path("user/<str:username>", views.user_view, name="user_view")
]
