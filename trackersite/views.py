import json
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from . import models
# Create your views here.

@login_required
def index(request):
    projects = models.Project.objects.filter()
    return render(request, "trackersite/index.html", {
        "projects": projects
    })
    

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
    return HttpResponseRedirect(reverse("login"))

@login_required
def create_project(request):
    if request.method == "POST":
        title = request.POST["title"].strip()
        desc = request.POST["desc"].strip()
        newProj = models.Project.objects.create(title = title, desc = desc)
        return HttpResponseRedirect("manage-project/{}".format(title))
    else:
        return render(request, "trackersite/newProject.html")
    
@login_required
def manage_project(request, name):
    project = models.Project.objects.get(title = name)
    team = models.Team.objects.filter(project_id = project.id).order_by('member__role')
    users = models.User.objects.exclude(id__in=
        models.Team.objects.filter(project_id = project.id).values_list('member_id', flat=True))
    print(users)
    return render(request, 'trackersite/manageProject.html', {
        "project": project, "members":users, "team":team
    })

@login_required
def manage_users(request):
    if request.method == "POST":
        pass
    else:    
        if request.user.role != "Admin":
            return HttpResponseRedirect(reverse("index"))
        else:
            users = models.User.objects.filter().order_by("id")
            return render(request, 'trackersite/users.html', {
                "users":users
            })

@login_required
def create_ticket(request):
    if request.method == "GET":
        return render(request, "trackersite/newTicket.html")
    else:
        pass
    
@login_required
def tickets(request):
    myTickets = models.Ticket.objects.filter(submitter_id = request.user.id).order_by('timestamp')
    return render(request, 'trackersite/myTickets.html', {
        "tickets": myTickets
    })

@login_required
def load_ticket(request, id):
    ticket = models.Ticket.objects.get(id = id)
    comments = models.Comment.objects.filter(ticket_id = id)
    return render(request, 'trackersite/ticket.html', {
        "ticket":ticket, "comments":comments,
    })

@login_required
def update_ticket(request):
    if request.method == "POST":
        print("post", request.POST)
        id = request.POST["id"]
        desc = request.POST["desc"]
        priority = request.POST["priority"]
        status = request.POST["status"]
        type = request.POST["type"]

        ticket = models.Ticket.objects.get(id = id)
        ticket.desc = desc
        ticket.priority = priority
        ticket.status = status
        ticket.type = type
        ticket.save()

        return HttpResponseRedirect(f"tickets/{id}")
    else:
        print(request.GET)
        id = request.GET["id"]
        ticket = models.Ticket.objects.get(id = id)
        
        # create and pass in lists to select html option
        priorities = [ "Low", "Medium", "High", "Urgent"]
        statuses = [ "New", "Open", "In Progress", "Resolved"]
        types = [ "Bug/Errors", "Features", "General Comments"]

        return render(request, 'trackersite/updateTicket.html', {
            "ticket":ticket, "priorities": priorities, "statuses":statuses, "types":types
        })

def create_comment(request):
    print(request.GET)
    id = request.GET["id"]
    comment = request.GET["comment"]
    models.Comment.objects.create(ticket_id = id, commenter_id = request.user.id, comment = comment)

    return HttpResponseRedirect(f"tickets/{id}")

# Fetch Functions
@login_required
def add_team_member(request):
    body = json.loads(request.body.decode("utf-8"))
    project_id = body["project_id"]
    try:
        user_id = models.User.objects.get(username=body["user"]).id
    except:
        return HttpResponse(status=400)
    print(project_id, user_id)
    member = models.Team.objects.create(project_id=project_id, member_id=user_id)
    print("new member made")
    return HttpResponse(status=201)

@login_required
def project_status(request):
    body = json.loads(request.body.decode("utf-8"))
    project_id = body["project_id"]
    new_status = body["status"]

    project = models.Project.objects.get(id = project_id)
    project.active = new_status
    project.save()

    return HttpResponse(status=204)

@login_required
def change_role(request):
    body = json.loads(request.body.decode("utf-8"))
    id = body["id"]
    role = body["role"]
    user = models.User.objects.get(id = id)
    user.role = role
    user.save()
    print("done")
    return HttpResponse(status=200)

@login_required
def remove_user(request):
    # Select User from fetched id and delete table row 
    body = json.loads(request.body.decode("utf-8"))
    id = body["id"]
    models.User.objects.get(id = id).delete()
    return HttpResponse(status=200)

def testpage(request):
    return render(request, 'trackersite/jibberjabber.html')