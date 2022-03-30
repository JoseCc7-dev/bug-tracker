from django.urls import path

from . import views
from django.views.generic.base import RedirectView

urlpatterns = [
    path("favicon.ico", RedirectView.as_view(url='/static/trackersite/favicon.ico')),
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("register", views.register_view, name="register"),
    path("logout", views.logout_view, name="logout"),
    path("create-project", views.create_project, name="create_project"),
    path("manage-project/<str:name>", views.manage_project, name="manage_project"),
    path("new-ticket", views.create_ticket, name="new_ticket"),
    path("manage-users", views.manage_users, name="manage_users"),
        
    # API route(s)
    path("add-member", views.add_team_member, name="add_member"),
    path("set-status", views.project_status, name="set_status"),
    path("change-role", views.change_role, name="change_role"),
    path("remove-user", views.remove_user, name="remove_user")
]