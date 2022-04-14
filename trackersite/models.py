from django.db import models

from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    email = models.EmailField(blank=True, max_length=254, verbose_name='email address', unique=True)
    class Role(models.TextChoices):
        DEV = "Developer", "Developer"
        MANG = "Manager", "Manager"
        ADMN = "Admin", "Admin"
    role = models.CharField(max_length=9, choices=Role.choices, default=Role.DEV)

class Project(models.Model):
    title = models.CharField(max_length=30)
    desc = models.TextField(max_length=600)

    class Status(models.TextChoices):
        NOT = "Not Started",
        PRGRS = "In Progress",
        CMPLTE = "Complete", 
    status = models.CharField(max_length=11, choices=Status.choices, default=Status.NOT)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="project_manager", null=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    time_created = models.DateTimeField(auto_now_add=True)

class Team(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    

class Ticket(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    submitter = models.ForeignKey(User, on_delete=models.CASCADE)
    desc = models.TextField(max_length=400)

    class Priority(models.TextChoices):
        LOW = "Low", 
        MEDIUM = "Medium", 
        HIGH = "High", 
        URGENT = "Urgent", 
    priority = models.CharField(max_length=6, choices=Priority.choices, default=Priority.LOW)

    class Status(models.TextChoices):
        NEW = "New", 
        OPEN = "Open", 
        RSLVD = "Resolved", 
        PRGRS = "In Progress", 
    status = models.CharField(max_length=11, choices=Status.choices, default=Status.NEW)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Types(models.TextChoices):
        BUGS = "Bug/Errors", 
        FEAT = "Features", 
        COMM = "General Comments",  
    type = models.CharField(max_length=16, choices=Types.choices, default=Types.BUGS)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="assigned_user")

class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.CharField(max_length=40)
    timestamp = models.DateTimeField(auto_now_add=True)

class History(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    value_field = models.CharField(max_length=9)
    value_old = models.TextField(null=True)
    value_new = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

# class Organization(models.Model):
    # 