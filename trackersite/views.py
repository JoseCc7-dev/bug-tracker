from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout

from . import models
# Create your views here.

def index(request):
    if request.user.is_authenticated:
        return render(request, "trackersite/index.html")
    else:
        print(request.user)
        return HttpResponseRedirect(reverse("login"))


def login_view(request):
    if request.method == "POST":
        username = request.POST["userName"]
        password = request.POST["password"]
        user = authenticate(request, username = username, password = password)
        
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "trackersite/login.html", {
                "message":"Invalid Username and/or Password."
            })
    else:
        return render(request, "trackersite/login.html")

def register_view(request):
    if request.method == "POST":
        print(request.POST['email'])
        username = request.POST['userName']
        email = request.POST['email']
        password = request.POST['password']
        confirm = request.POST['confirmPassword']
        try:
            try:
                user = models.User.objects.get(username = username)
                return render(request, "trackersite/register.html", {
                "message": "Username already taken."
            })
            except:
                pass
            email = models.User.objects.get(email = email)
            return render(request, "trackersite/register.html", {
                "message": "Account with email already exists"
            })
        except:
            if password != confirm:
                print("passwords don't match")
                return render(request, "trackersite/register.html", {
                "message": "Passwords do not match"
                })
            else:
                user = models.User.objects.create_user(username = username, email = email, password = password)
                login(request, user)
                return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "trackersite/register.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect("login")