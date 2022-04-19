from django.urls import path
from django.views.generic.base import RedirectView
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    path("favicon.ico", RedirectView.as_view(url='/static/trackersite/favicon.ico')),
    path("", views.index, name="index"),
    
    # acct creation/login & activation 
    path("login", views.login_view, name="login"),
    path("register", views.register_view, name="register"),
    path("logout", views.logout_view, name="logout"),
    path("forgot", views.forgot, name="forgot"),
    path("activate/<str:uidb64>/<str:token>", views.activate, name="activate"),
    path("password_reset/<str:uidb64>/<str:token>", views.password_reset, name="reset_password"),
    
    # project urls
    path("create-project", views.create_project, name="create_project"),
    path("manage-project/<str:name>", views.manage_project, name="manage_project"),
    path("my-projects", views.projects, name="my_projects"),
    path("update-project", views.update_project, name="update_project"),
    path("delete-project", views.delete_project, name="delete_project"),
    
    # user urls
    path("manage-users", views.manage_users, name="manage_users"),
    path("user/<str:name>", views.load_user, name="load_user"), 
    
    
    # ticket urls
    path("new-ticket", views.create_ticket, name="new_ticket"),
    path("my-tickets", views.tickets, name="my_tickets"),
    path("tickets/<int:id>", views.load_ticket, name="load_ticket"),
    path("update-ticket", views.update_ticket, name="update_ticket"),
    path("delete-ticket", views.delete_ticket, name="delete_ticket"),
    path("comment", views.create_comment, name="create_comment"),

        
    # API route(s)
    path("add-member", views.add_team_member, name="add_member"),
    path("set-status", views.project_status, name="set_status"),
    path("change-role", views.change_role, name="change_role"),
    path("delete-user", views.delete_user, name="delete_user"),
    path("remove-user", views.remove_member, name="remove_member" ),

    path("test", views.testpage)
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)