import json
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.db.models import Q

from . import models
# Create your views here.

# TODO
# email verif
# password reset
# ui's index,
# user pages self & others


@login_required
def index(request):
    # Get all active projects related to user
    projects = models.Project.objects.filter(Q(id__in= 
        models.Team.objects.filter(member_id = request.user.id).values_list('project_id')) & Q(status__in= ["In Progress", "Not Started"])).order_by('time_created')

    # Get values list of projects for tickets
    list = models.Team.objects.filter(member_id = request.user.id).values_list('project_id')

    # Get all unresolved tickets for projects related to user
    tickets = models.Ticket.objects.filter(Q(project_id__in= list) & Q(status__in= ["New", "Open", "In Progress"])).order_by('project_id')

    print("list:", list)
    print("tickets:", tickets)
    return render(request, "trackersite/index.html", {
        "projects": projects, "tickets":tickets
    })
    

def login_view(request):
    if request.method == "POST":
        username = request.POST["userName"].capitalize()
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
        username = request.POST['userName'].capitalize()
        user_email = request.POST['email']
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
            email = models.User.objects.get(email = user_email)
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
                user = models.User.objects.create_user(username = username, email = user_email, password = password)
                user.is_active = False
                user.save()
                current_site = get_current_site(request)
                mail_subject = 'Activate your Harmonic account.'
                message = render_to_string('trackersite/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
                })
                to_email = user_email
                email = EmailMessage(
                            mail_subject, message, to=[to_email]
                )
                email.send()
                return render(request, 'trackersite/confirm.html')
    else:
        return render(request, "trackersite/register.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))

def forgot(request):
    if request.method == 'GET':
        return render(request, 'trackersite/forgot.html')
    else:
        user_email = request.POST['email']
        print(user_email)
        try:
            user = models.User.objects.get(email = user_email)
        except:
            # if no acct found for email return no user found page
            return render(request, 'trackersite/noUser.html')
        current_site = get_current_site(request)
        mail_subject = 'Activate your Harmonic account.'
        message = render_to_string('trackersite/reset_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid':urlsafe_base64_encode(force_bytes(user.pk)),
        'token':account_activation_token.make_token(user),
        })
        to_email = user_email
        email = EmailMessage(
                    mail_subject, message, to=[to_email]
        )
        email.send()
        print(user_email)
        return render(request, 'trackersite/sentEmail.html', {
            "email":user_email
        })

def password_reset(request, uidb64=None, token=None):
    if request.method == "GET":
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = models.User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, models.User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            return render(request, 'trackersite/changePassword.html', {
                "name":user.username
            })
    else:
        name = request.POST["name"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]
        if password == confirm_password:
            user = models.User.objects.get(username = name)
            user.set_password(password)
            user.save()
        print("password:",password,"Cpassword:",confirm_password)
        
        return HttpResponse('password changed')

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = models.User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, models.User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return render(request, 'trackersite/activated.html')
    else:
        return HttpResponse('Activation link is invalid!')

@login_required
def create_project(request):
    if request.method == "POST":
        title = request.POST["title"].strip()
        desc = request.POST["desc"].strip()
        creator = request.user.id
        models.Project.objects.create(title = title, desc = desc, creator_id = creator)
        return HttpResponseRedirect("manage-project/{}".format(title))
    else:
        return render(request, "trackersite/newProject.html")
    
@login_required
def manage_project(request, name):
    project = models.Project.objects.get(title = name)
    team = models.Team.objects.filter(project_id = project.id).order_by('member__role')
    users = models.User.objects.exclude(id__in=
        models.Team.objects.filter(project_id = project.id).values_list('member_id', flat=True))
    tickets = models.Ticket.objects.filter(project_id = project.id, status__in = ["New","Open","In Progress",])
    print(tickets)
    print(users)
    return render(request, 'trackersite/manageProject.html', {
        "project": project, "members":users, "team":team, "tickets":tickets
    })

@login_required
# load projects page
def projects(request):
    if request.user.role != "Developer":
        projects = models.Project.objects.filter(id__in= 
        models.Team.objects.filter(member_id = request.user.id).values_list('project_id')).order_by('time_created')
        
        allProjects = models.Project.objects.filter().order_by('time_created')

        return render(request, 'trackersite/myProjects.html', {
            "projects":projects, "allProjects":allProjects
        }) 
    else:
        projects = models.Project.objects.filter(id__in= 
        models.Team.objects.filter(member_id = request.user.id).values_list('project_id')).order_by('time_created')
        print(projects)
        return render(request, 'trackersite/myProjects.html', {
            "projects":projects
        })

@login_required
def update_project(request):
    if request.method == "GET":
        id = request.GET["id"]
        project = models.Project.objects.get(id = id)

        statuses = ["Not Started", "In Progress", "Complete"]

        print(project.manager)
        return render(request, 'trackersite/updateProject.html', {
            "project":project, "statuses":statuses
        })
    else:
        print(request.POST)

        id = request.POST["id"]
        title = request.POST["title"]
        desc = request.POST["desc"]
        status = request.POST["status"]

        project = models.Project.objects.get(id = id)

        project.title = title
        project.desc = desc
        project.status = status
        project.save()

        return HttpResponseRedirect(f"manage-project/{project.title}")

@login_required
def delete_project(request):
    id = request.POST['id']
    models.Project.objects.get(id = id).delete()

    return HttpResponseRedirect("my-projects")

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
def load_user(request, name = None):
    if request.method == "GET":
        try:
            user = models.User.objects.get(username = name)
        except:
            return HttpResponseBadRequest()
        
        if user == request.user:
            return render(request, 'trackersite/loadSelf.html', {
                'loaduser':user
            })
        else:
            return render(request, 'trackersite/loadUser.html', {
                'loaduser':user
            })
    # Can only make POST request on own profile page
    else:    
        username = request.POST["username"].capitalize()
        first_name = request.POST["first_name"].capitalize()
        last_name = request.POST["last_name"].capitalize()
        print(username, first_name, last_name)
        
        user = models.User.objects.get(id = request.user.id)
        user.first_name = first_name
        user.last_name = last_name
        try:
            
            user.username = username
            user.save()
        except:
            print("request", request.user)
            print("user", user)
            return render(request, 'trackersite/loadSelf.html', {
                "loaduser":user, "message":"Username already taken."
            })
        request.user = user
        return render(request, 'trackersite/loadSelf.html', {
            "loaduser":user
        }) 


@login_required
def create_ticket(request):
    if request.method == "GET":
        # On GET load new ticket template
        id = request.GET["id"]
        return render(request, "trackersite/newTicket.html", {
            "id":id
        })
    else:
        # On POST create ticket then redirect to project
        print(request.POST)
        id = request.POST['project_id']
        title = request.POST['title']
        submitter = request.user.id
        desc = request.POST['project_id']
        priority = request.POST['priority']
        type = request.POST['type']

        models.Ticket.objects.create(project_id = id, title = title, submitter = request.user, desc = desc, priority = priority, type = type)

        project_title = models.Project.objects.get(id = id).title

        return HttpResponseRedirect("manage-project/"+ project_title)
    
@login_required
def tickets(request):
    myTickets = models.Ticket.objects.filter(Q(submitter_id = request.user.id) | Q(assigned_to = request.user.id)).order_by('timestamp')
    allTickets = models.Ticket.objects.filter().order_by('timestamp')
    return render(request, 'trackersite/myTickets.html', {
        "tickets": myTickets, "allTickets": allTickets,
    })

@login_required
def load_ticket(request, id):
    ticket = models.Ticket.objects.get(id = id)
    comments = models.Comment.objects.filter(ticket_id = id)
    history = models.History.objects.filter(ticket_id = id)

    return render(request, 'trackersite/ticket.html', {
        "ticket":ticket, "comments":comments, "history":history
    })

@login_required
def update_ticket(request):
    if request.method == "POST":
        print("post", request.POST)
        id = request.POST["id"]
        title = request.POST["title"]
        desc = request.POST["desc"]
        priority = request.POST["priority"]
        status = request.POST["status"]
        type = request.POST["type"]
        assigned_to = request.POST["assigned"]

        # create ticket history object

        ticket = models.Ticket.objects.get(id = id)
        if ticket.title != title:
            models.History.objects.create(ticket_id = id, value_field = "Title", value_old = ticket.title, value_new = title)
            ticket.title = title
        
        if ticket.desc != desc:
            models.History.objects.create(ticket_id = id, value_field = "Desc", value_old = ticket.desc, value_new = desc)
            ticket.desc = desc
        
        if ticket.priority != priority:
            models.History.objects.create(ticket_id = id, value_field = "Priority", value_old = ticket.priority, value_new = priority)
            ticket.priority = priority

        if ticket.status != status:
            models.History.objects.create(ticket_id = id, value_field = "Status", value_old = ticket.status, value_new = status)
            ticket.status = status

        if ticket.type != type:
            models.History.objects.create(ticket_id = id, value_field = "Type", value_old = ticket.type, value_new = type)
            ticket.type = type

        if ticket.assigned_to != assigned_to:
            user = models.User.objects.get(username = assigned_to)
            models.History.objects.create(ticket_id = id, value_field = "Assigned", value_old = ticket.assigned_to, value_new = user)
            ticket.assigned_to = user

        ticket.save()


        return HttpResponseRedirect(f"tickets/{id}")
    else:
        print(request.GET)
        id = request.GET["id"]
        ticket = models.Ticket.objects.get(id = id)
        users = models.User.objects.filter()

        # create and pass in lists to select html option
        priorities = [ "Low", "Medium", "High", "Urgent"]
        statuses = [ "New", "Open", "In Progress", "Resolved"]
        types = [ "Bug/Errors", "Features", "General Comments"]

        return render(request, 'trackersite/updateTicket.html', {
            "ticket":ticket, "priorities": priorities, "statuses":statuses, "types":types, "users":users
        })

@login_required
def delete_ticket(request):

    id = request.POST['id']
    models.Ticket.objects.get(id=id).delete()

    return HttpResponseRedirect("my-tickets")

def create_comment(request):
    print(request.POST)
    id = request.POST["id"]
    comment = request.POST["comment"]
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
def delete_user(request):
    # Select User from fetched id and delete table row 
    body = json.loads(request.body.decode("utf-8"))
    id = body["id"]
    models.User.objects.get(id = id).delete()
    return HttpResponse(status=200)

@login_required
def remove_member(request):
    body = json.loads(request.body.decode("utf-8"))
    member_id = body["member_id"]
    print("row:", member_id)
    models.Team.objects.get(id = member_id).delete()
    print("deleted")
    return HttpResponse(status=200)

def testpage(request):
    return render(request, 'trackersite/welcome.html')