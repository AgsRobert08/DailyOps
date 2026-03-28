from django.urls import path
from . import views

app_name = "whatsapp"

urlpatterns = [
    # Interfaz
    path("", views.inbox, name="inbox"),
    path("conversacion/<int:conversation_id>/", views.conversation_detail, name="conversation"),

    # API interna (usada por JS del frontend)
    path("api/conversacion/<int:conversation_id>/enviar/", views.send_message, name="send_message"),
    path("api/conversacion/<int:conversation_id>/mensajes/", views.poll_messages, name="poll_messages"),

    # Webhook de yCloud
    path("webhook/ycloud/", views.ycloud_webhook, name="ycloud_webhook"),
]