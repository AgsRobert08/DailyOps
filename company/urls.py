from django.urls import path
from . import views

app_name = "company"

urlpatterns = [
    # Auth
    path("",        views.login_view,  name="login"),
    path("logout/", views.logout_view, name="logout"),

    # Dashboard
    path("dashboard/", views.dashboard, name="dashboard"),

    # Empresa
    path("empresa/", views.company_settings, name="company_settings"),

    # Usuarios
    path("usuarios/",               views.users_list,  name="users_list"),
    path("usuarios/nuevo/",         views.user_create, name="user_create"),
    path("usuarios/<int:pk>/",      views.user_edit,   name="user_edit"),
    path("usuarios/<int:pk>/eliminar/", views.user_delete, name="user_delete"),
]