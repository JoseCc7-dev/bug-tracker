import json
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.db.models import Q
from django.core.files.storage import FileSystemStorage

from . import models
# Create your views here.

def isAdmin(user):
    if user.role == 'Admin':
        return True
    else:
        return False

def isNotDeveloper(user):
    if user.role != 'Developer':
        return True
    else:
        return False

@login_required
def index(request):
    # Get all active projects related to user
    projects = models.Project.objects.filter(Q(id__in= 
        models.Team.objects.filter(member_id = request.user.id).values_list('project_id')) & Q(status__in= ["In Progress", "Not Started"])).order_by('time_created')

    # Get values list of projects for tickets
    list = models.Team.objects.filter(member_id = request.user.id).values_list('project_id')

    # Get all unresolved tickets for projects related to user
    tickets = models.Ticket.objects.filter(Q(project_id__in= list) & Q(status__in= ["New", "Open", "In Progress"])).order_by('project_id')

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

def login_demo_user(request):
    if request.method == "GET":
        return render(request, 'trackersite/demo_user_login.html')
    else:
        role = request.POST["role"]
        user = models.User.objects.get(username = f"Demo_{role}_acct".capitalize())
        login(request, user)
        return HttpResponseRedirect(reverse("index"))

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
        try:
            user = models.User.objects.get(email = user_email)
        except:
            # if no acct found for email return no user found page
            return render(request, 'trackersite/no_user.html')
        current_site = get_current_site(request)
        mail_subject = 'Change your Harmonic account password.'
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
        return render(request, 'trackersite/sent_email.html', {
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
            return render(request, 'trackersite/change_password.html', {
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
        
        return render(request, 'trackersite/login.html', {
            "message":"New Password Set"
        })

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

# Manager or higher required to view this page
@login_required
def create_project(request):
    if request.user.role == 'Developer':
        return HttpResponseRedirect(reverse("index"))

    if request.method == "POST":
        # Stop Demo User Changes
        if request.user.demo_user == True:
            return HttpResponseRedirect(reverse("index"))
        else:
            title = request.POST["title"].strip()
            desc = request.POST["desc"].strip()
            creator = request.user.id
            models.Project.objects.create(title = title, desc = desc, creator_id = creator)
            return HttpResponseRedirect("manage-project/{}".format(title))
    else:
        return render(request, "trackersite/new_project.html")
    
@login_required
def manage_project(request, name):
    project = models.Project.objects.get(title = name)
    team = models.Team.objects.filter(project_id = project.id).order_by('member__role')
    users = models.User.objects.exclude(id__in=
        models.Team.objects.filter(project_id = project.id).values_list('member_id', flat=True))
    tickets = models.Ticket.objects.filter(project_id = project.id, status__in = ["New","Open","In Progress",])
    return render(request, 'trackersite/manage_project.html', {
        "project": project, "members":users, "team":team, "tickets":tickets
    })

# load projects page
@login_required
def projects(request):
    if request.user.role != "Developer":
        projects = models.Project.objects.filter(id__in= 
        models.Team.objects.filter(member_id = request.user.id).values_list('project_id')).order_by('time_created')
        
        allProjects = models.Project.objects.filter().order_by('time_created')

        return render(request, 'trackersite/my_projects.html', {
            "projects":projects, "allProjects":allProjects
        }) 
    else:
        projects = models.Project.objects.filter(id__in= 
        models.Team.objects.filter(member_id = request.user.id).values_list('project_id')).order_by('time_created')
        return render(request, 'trackersite/my_projects.html', {
            "projects":projects
        })

# Manager or higher required to view this page
@login_required
def update_project(request):
    if request.user.role == "Developer":
        return HttpResponseRedirect(reverse("index"))

    if request.method == "GET":
        id = request.GET["id"]
        project = models.Project.objects.get(id = id)

        statuses = ["Not Started", "In Progress", "Complete"]

        return render(request, 'trackersite/update_project.html', {
            "project":project, "statuses":statuses
        })
    else:
        id = request.POST["id"]
        title = request.POST["title"]
        desc = request.POST["desc"]
        status = request.POST["status"]

        project = models.Project.objects.get(id = id)

        # stop Demo user changes
        if request.user.demo_user == True:
            return HttpResponseRedirect(f"manage-project/{project.title}")

        project.title = title
        project.desc = desc
        project.status = status
        project.save()

        return HttpResponseRedirect(f"manage-project/{project.title}")

@login_required
def delete_project(request):
    if request.user.demo_user == True or request.user.role == "Developer":
        return HttpResponseRedirect("my-projects")

    id = request.POST['id']
    models.Project.objects.get(id = id).delete()

    return HttpResponseRedirect("my-projects")

@login_required
def manage_users(request):
    if request.user.role != "Admin":
        return HttpResponseRedirect(reverse("index"))
    else:
        users = models.User.objects.filter().order_by("username")
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
        # load own page
        if user == request.user:
            return render(request, 'trackersite/load_self.html', {
                'loaduser':user
            })
        # load other user's page
        else:
            try:
                projects = models.Project.objects.filter(id__in= 
                    models.Team.objects.filter(member_id = user.id).values_list('project_id')).order_by('time_created')
            except:
                projects = None
            try:
                tickets = models.Ticket.objects.filter(Q(submitter_id = user.id) | Q(assigned_to = user.id)).order_by('timestamp')
            except:
                tickets = None
            
            return render(request, 'trackersite/load_user.html', {
                'loaduser':user, 'projects':projects, 'tickets':tickets
            })
    # Can only make POST request on own profile page
    else:    
        if request.user.demo_user == True:
            return HttpResponseRedirect(f"{request.user}")

        username = request.POST["username"].capitalize()
        first_name = request.POST["first_name"].capitalize()
        last_name = request.POST["last_name"].capitalize()
        
        user = models.User.objects.get(id = request.user.id)
        user.first_name = first_name
        user.last_name = last_name
        try:
            
            user.username = username
            user.save()
        except:
            return render(request, 'trackersite/load_self.html', {
                "loaduser":user, "message":"Username already taken."
            })
        request.user = user
        return HttpResponseRedirect(f"{request.user}")

@login_required
def new_password(request):
    if request.method == "GET":
        return render(request, 'trackersite/new_password.html')
    else:
        if request.user.demo_user == True:
            return HttpResponseRedirect(f"user/{request.user}")

        old_password = request.POST["old_password"]
        new_password = request.POST["new_password"]
        confirm = request.POST["confirm"]

        user = authenticate(request, username = request.user.username, password = old_password)

        if user is not None:
            if new_password == confirm:
                user.set_password(new_password)
                user.save()
                login(request, user)
                return render(request, 'trackersite/load_self.html', {
                    "password_message":"Password Updated.", "loaduser":user
                })
            else:
                return render(request, 'trackersite/new_password.html', {
                    "message2":"Passwords do not match."
                })
        else:
            return render(request, 'trackersite/new_password.html', {
                "message1":"Incorrect Password."
            })

@login_required
def change_email_request(request):
    if request.method == "GET":
        return render(request, 'trackersite/change_email.html')
    else:
        if request.user.demo_user == True:
            return HttpResponseRedirect(f"user/{request.user}")

        user = models.User.objects.get(id = request.user.id)
        current_site = get_current_site(request)
        mail_subject = 'Change your Harmonic account email address.'
        message = render_to_string('trackersite/change_address_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid':urlsafe_base64_encode(force_bytes(user.pk)),
        'token':account_activation_token.make_token(user),
        })
        to_email = user.email
        email = EmailMessage(
                    mail_subject, message, to=[to_email]
        )
        email.send()
        return render(request, 'trackersite/change_address_sent.html', {
            "email":user.email
        })

def new_email(request, uidb64=None, token=None):
    if request.method == "GET":
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = models.User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, models.User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            login(request, user)
            return render(request, 'trackersite/new_email.html')
        else:
            return HttpResponse('Activation link is invalid!')
    else:
        new_email = request.POST["new_email"]
        user = models.User.objects.get(id = request.user.id)
        current_site = get_current_site(request)
        mail_subject = 'Confirm Harmonic account email change.'
        message = render_to_string('trackersite/new_address_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid':urlsafe_base64_encode(force_bytes(user.pk)),
        'token':account_activation_token.make_token(user),
        })
        to_email = new_email
        email = EmailMessage(
                    mail_subject, message, to=[to_email]
        )
        email.send()
        return render(request, 'trackersite/change_address_sent.html', {
            "email":new_email
        })

def change_account_email(request, uidb64=None, token=None):
    if request.method == "GET":
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = models.User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, models.User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            return render(request, 'trackersite/change_account_email.html', {
                "id":user.id
            })
        else:
            return HttpResponse('Activation link is invalid!')
    else:
        new_email = request.POST['new_email']
        password = request.POST['password']
        uid = request.POST['id']
        name = models.User.objects.get(id = uid).username
        user = authenticate(request, username = name, password = password)
        
        if user is not None:
                user.email = new_email
                user.save()
                login(request, user)
                return render(request, 'trackersite/load_self.html', {
                    "email_message":"Email Address Updated.", "loaduser":user
                })
        else:
            return render(request, 'trackersite/change_account_email.html', {
                "message":"Incorrect Password.", "id":uid
            })

@login_required
def change_picture(request):
    if request.method == "POST" and request.FILES['image_file']:
        if request.user.demo_user == True:
            return HttpResponseRedirect(f"user/{request.user}")

        myfile = request.FILES['image_file']
        fs = FileSystemStorage(location='media/covers')
        fs.save(myfile.name, myfile)
        uploaded_file_url = "covers/"+ myfile.name

        user = request.user
        user.image.delete()
        user.image = uploaded_file_url
        user.save()
        return HttpResponseRedirect(f'user/{user.username}')
    else:
        return render(request, 'trackersite/new_picture.html')
        

@login_required
def create_ticket(request):
    if request.method == "GET":
        # On GET load new ticket template
        id = request.GET["id"]
        return render(request, "trackersite/new_ticket.html", {
            "id":id
        })
    else:
        # On POST create ticket then redirect to project
        id = request.POST['project_id']
        title = request.POST['title']
        desc = request.POST['desc']
        priority = request.POST['priority']
        type = request.POST['type']
        
        project_title = models.Project.objects.get(id = id).title
        
        if request.user.demo_user == True:
            return HttpResponseRedirect(f"manage-project/{project_title}")
        
        models.Ticket.objects.create(project_id = id, title = title, submitter = request.user, desc = desc, priority = priority, type = type)

        return HttpResponseRedirect(f"manage-project/{project_title}")
    
@login_required
def tickets(request):
    myTickets = models.Ticket.objects.filter(Q(submitter_id = request.user.id) | Q(assigned_to = request.user.id)).order_by('timestamp')
    allTickets = models.Ticket.objects.filter().order_by('timestamp')
    return render(request, 'trackersite/my_tickets.html', {
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
        # get form info
        id = request.POST["id"]
        title = request.POST["title"]
        desc = request.POST["desc"]
        priority = request.POST["priority"]
        status = request.POST["status"]
        type = request.POST["type"]
        assigned_to = request.POST["assigned"]

        if request.user.demo_user == True:
            return HttpResponseRedirect(f"tickets/{id}")

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

        # redirect to updated ticket page

        return HttpResponseRedirect(f"tickets/{id}")
    else:
        # get ticket 

        id = request.GET["id"]
        ticket = models.Ticket.objects.get(id = id)
        users = models.User.objects.filter().order_by("username")

        # create and pass in lists to select html option
        priorities = [ "Low", "Medium", "High", "Urgent"]
        statuses = [ "New", "Open", "In Progress", "Resolved"]
        types = [ "Bug/Errors", "Features", "General Comments"]

        return render(request, 'trackersite/update_ticket.html', {
            "ticket":ticket, "priorities": priorities, "statuses":statuses, "types":types, "users":users
        })

@login_required
def delete_ticket(request):

    if request.user.demo_user == True:
        return HttpResponseRedirect("my-tickets")

    id = request.POST['id']
    models.Ticket.objects.get(id=id).delete()

    return HttpResponseRedirect("my-tickets")

@login_required
def create_comment(request):
    id = request.POST["id"]
    comment = request.POST["comment"]
    
    if request.user.demo_user == True:
        return HttpResponseRedirect(f"tickets/{id}")

    models.Comment.objects.create(ticket_id = id, commenter_id = request.user.id, comment = comment)

    return HttpResponseRedirect(f"tickets/{id}")

# Fetch Functions
@login_required
def add_team_member(request):
    if request.user.demo_user == True:
        return HttpResponse(status=201)

    body = json.loads(request.body.decode("utf-8"))
    project_id = body["project_id"]
    try:
        user_id = models.User.objects.get(username=body["user"]).id
    except:
        return HttpResponse(status=400)
    member = models.Team.objects.create(project_id=project_id, member_id=user_id)
    return HttpResponse(status=201)

@login_required
def change_role(request):
    if request.user.demo_user == True:
        return HttpResponse(status=200)

    body = json.loads(request.body.decode("utf-8"))
    id = body["id"]
    role = body["role"]
    user = models.User.objects.get(id = id)
    user.role = role
    user.save()
    return HttpResponse(status=200)

@login_required
def delete_user(request):
    if request.user.demo_user == True:
        return HttpResponse(status=200)

    # Select User from fetched id and delete table row 
    body = json.loads(request.body.decode("utf-8"))
    id = body["id"]
    models.User.objects.get(id = id).delete()
    return HttpResponse(status=200)

@login_required
def remove_member(request):
    if request.user.demo_user == True:
        return HttpResponse(status=200)

    body = json.loads(request.body.decode("utf-8"))
    member_id = body["member_id"]
    models.Team.objects.get(id = member_id).delete()
    return HttpResponse(status=200)
