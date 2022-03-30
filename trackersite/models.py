from django.db import models

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

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
    priority = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    ongoing = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now=True)

# class Organization(models.Model):
    # 