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

    path("calendar/",                          views.calendar_view,          name="calendar_view"),
    path("calendar/connect/",                  views.calendar_connect,        name="calendar_connect"),
    path("calendar/oauth/callback/", views.calendar_callback, name="calendar_callback"),    
    path("calendar/disconnect/",               views.calendar_disconnect,     name="calendar_disconnect"),
    path("calendar/webhook/",                  views.calendar_webhook,        name="calendar_webhook"),

    # API JSON para el frontend
    path("calendar/api/events/",               views.calendar_events_api,     name="calendar_events_api"),
    path("calendar/api/events/create/",        views.calendar_event_create,   name="calendar_event_create"),
    path("calendar/api/events/<str:event_id>/update/", views.calendar_event_update, name="calendar_event_update"),
    path("calendar/api/events/<str:event_id>/delete/", views.calendar_event_delete, name="calendar_event_delete"),
]