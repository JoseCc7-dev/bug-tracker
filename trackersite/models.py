from django.db import models

from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    pass

class Project(models.Model):
    title = models.CharField(max_length=50)
    manager = models.ForeignKey(User, ondelete=models.Cascade) 

class Team(models.Model):
    project = models.ForeignKey(Project, ondelete=models.Cascade)
    member = models.ForeignKey(User, ondelete=models.cascade)

class Bug (models.Model):
    title = models.CharField(max_length=50)
    submitter = models.ForeignKey(User, ondelete=models.Cascade)
    desc = models.CharField(max_length=400)
    priority = models.IntegerField(max=4)
    ongoing = models.BooleanField()
    timestamp = models.DateTimeField()
    