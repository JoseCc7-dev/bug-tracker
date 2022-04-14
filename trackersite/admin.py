from django.contrib import admin

from .models import User, Project, Team, Ticket, Comment, History
# Register your models here.
admin.site.register(User)
admin.site.register(Project)
admin.site.register(Team)
admin.site.register(Ticket)
admin.site.register(Comment)
admin.site.register(History)
