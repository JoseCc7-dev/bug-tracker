from django.db import models

from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    class Role(models.TextChoices):
        DEV = "Developer", "Developer"
        MANG = "Manager", "Manager"
        ADMN = "Admin", "Admin"
    role = models.CharField(max_length=9, choices=Role.choices, default=Role.DEV)

class Project(models.Model):
    title = models.CharField(max_length=30)
    desc = models.CharField(max_length=600)
    active = models.BooleanField(default=True)

class Team(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    

class Ticket(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    submitter = models.ForeignKey(User, on_delete=models.CASCADE)
    desc = models.CharField(max_length=400)

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
    timestamp = models.DateTimeField(auto_now=True)

    class Types(models.TextChoices):
        BUGS = "Bug/Errors", 
        FEAT = "Features", 
        COMM = "General Comments",  
    type = models.CharField(max_length=16, choices=Types.choices, default=Types.BUGS)

class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.CharField(max_length=40)
    timestamp = models.DateTimeField(auto_now=True)

# class Organization(models.Model):
    # 