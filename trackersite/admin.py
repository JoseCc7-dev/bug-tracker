from django.contrib import admin

from .models import User, Project, Team, Ticket, Comment, History
# Register your models here.
class TicketAdmin(admin.ModelAdmin):
    list_display = ('project','title', 'submitter', 'desc', 'priority', 'status', 'type', 'assigned_to', 'timestamp' )

admin.site.register(User)
admin.site.register(Project)
admin.site.register(Team)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Comment)
admin.site.register(History)
