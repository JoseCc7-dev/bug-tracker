import json
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout

from . import models
# Create your views here.

def index(request):
    if request.user.is_authenticated:
        print(request.GET)
        projects = models.Project.objects.filter()
        return render(request, "trackersite/index.html", {
            "projects": projects
        })
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


def create_project(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            title = request.POST["title"].strip()
            desc = request.POST["desc"].strip()
            newProj = models.Project.objects.create(title = title, desc = desc)
            return HttpResponseRedirect("manage-project/{}".format(title))
        else:
            return render(request, "trackersite/newProject.html")
    else:
        return HttpResponseRedirect(reverse("login"))

def create_ticket(request):
    pass

def manage_project(request, name):
    if request.user.is_authenticated:
        project = models.Project.objects.get(title = name)
        team = models.Team.objects.filter(project_id = project.id).order_by('-role')
        users = models.User.objects.exclude(id__in=
            models.Team.objects.filter(project_id = project.id).values_list('member_id', flat=True))
        print(users)
        return render(request, 'trackersite/manageProject.html', {
            "project": project, "members":users, "team":team
        })
    else:
        return HttpResponseRedirect(reverse("login"))    

def manage_users(request):
    pass

def add_team_member(request):
    body = json.loads(request.body.decode("utf-8"))
    project_id = body["project_id"]
    user_id = models.User.objects.get(username=body["user"]).id
    role = body["role"]
    print(project_id, user_id, role)
    member = models.Team.objects.create(project_id=project_id, member_id=user_id, role=role)
    print("new member made")
    return HttpResponse(status=204)