from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound

import re
import markdown2
import random

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })



def entry(request, entryTitle="Main_Page"):

    # Check if user went to wiki/ instead of wiki/TITLE
    if entryTitle == "Main_Page":
        return HttpResponseRedirect(reverse(index))

    article = util.get_entry(entryTitle)

    # Check if the article exist
    if not article:
        # if it doesnt then render the help part of enty.html
        return render(request, "encyclopedia/entry.html",{
        "title": entryTitle,
        "message": article
    })
    
    # render the article
    return render(request, "encyclopedia/entry.html",{
        "title": entryTitle,
        "article": markdown2.markdown(article) # using the markdown2 lib
    })

def search(request):
    # Get the query from the url
    query = str(request.GET.get("q"))

    # check if user input anything
    if not query:
        return render(request, "encyclopedia/search.html", {
            "title": query,
            "results": query
        })
    
    # Check if query contains the follow special characters ", ' 
    if re.search(r"[\"\']", query):
        return render(request, "encyclopedia/search.html", {
            "title": query,
            "message": True
        })

    # Check if the artice exists and rediect to the artice if it does
    if util.get_entry(query):
        return HttpResponseRedirect(reverse(entry) + query)
    

    return render(request, "encyclopedia/search.html", {
        "title": query,
        "results": util.search_entries(query)
    })

def new_entry(request):
    if request.method == "POST":

        # Check if user submitted a title
        if not request.POST.get("title"):
            return render(request, "encyclopedia/new.html", {
                "message": "Invalid Title!"
            })
        
        # Check if user submitted any content
        if not request.POST.get("article"):
            return render(request, "encyclopedia/new.html", {
                "message": "Invalid Article!"
            })
        
        title = request.POST.get("title")
        article = request.POST.get("article")
        
        # Check if the title include special characters
        if  re.search(r"[\"\']", title):
            return render(request, "encyclopedia/new.html", {
                "message": "Invalid Title!"
            })
        
        # Check if file exists 
        if util.get_entry(title):
             return render(request, "encyclopedia/new.html", {
                "message": "Article Exists!"
            })
        
        util.save_entry(title, bytes(article,"utf-8"))
        return HttpResponseRedirect(reverse("entry") + title)
        
    return render(request, "encyclopedia/new.html")

def random_entry(request):
    entries = util.list_entries()
    rand = random.randint(0, len(entries)-1)
    return HttpResponseRedirect(reverse("entry") + entries[rand])

def edit_entry(request, entryTitle="Main_Page"):

    if entryTitle == "Main_Page":
        return HttpResponseRedirect(reverse(index))

    content = util.get_entry(entryTitle)  #store content of the entry
    if not content:
        return HttpResponseNotFound("Page not found")
    
    

    
    if request.method == "POST":
        title = request.POST.get("title")
        article = request.POST.get("article")

        if title != entryTitle:
            return render(request, "encyclopedia/edit.html",{
            "title": entryTitle,
            "content": article
        })

        if not util.get_entry(title):
            return HttpResponseRedirect(reverse("index"))
        
        util.save_entry(entryTitle, bytes(article, "utf-8"))
        return HttpResponseRedirect(reverse("entry") + entryTitle)

            

    
    return render(request, "encyclopedia/edit.html",{
        "title": entryTitle,
        "content": content
    })