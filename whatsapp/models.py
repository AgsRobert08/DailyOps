from django.db import models
from django.utils import timezone


class Contact(models.Model):
    phone = models.CharField(max_length=30, unique=True, verbose_name="Teléfono")
    name = models.CharField(max_length=120, blank=True, verbose_name="Nombre")
    avatar_initials = models.CharField(max_length=3, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.name:
            parts = self.name.strip().split()
            self.avatar_initials = "".join(p[0].upper() for p in parts[:2])
        else:
            self.avatar_initials = self.phone[-2:]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name or self.phone

    class Meta:
        verbose_name = "Contacto"
        verbose_name_plural = "Contactos"


class Conversation(models.Model):
    STATUS_CHOICES = [
        ("open", "Abierta"),
        ("closed", "Cerrada"),
    ]
    contact = models.OneToOneField(Contact, on_delete=models.CASCADE, related_name="conversation")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="open")
    unread_count = models.PositiveIntegerField(default=0)
    last_message_at = models.DateTimeField(default=timezone.now)
    last_message_preview = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conv con {self.contact}"

    class Meta:
        ordering = ["-last_message_at"]
        verbose_name = "Conversación"
        verbose_name_plural = "Conversaciones"


class Message(models.Model):
    DIRECTION_CHOICES = [
        ("inbound", "Entrante"),
        ("outbound", "Saliente"),
    ]
    STATUS_CHOICES = [
        ("sending", "Enviando"),
        ("sent", "Enviado"),
        ("delivered", "Entregado"),
        ("read", "Leído"),
        ("failed", "Fallido"),
    ]

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    ycloud_message_id = models.CharField(max_length=100, blank=True, db_index=True)
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    body = models.TextField(verbose_name="Mensaje")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="sending")
    timestamp = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]
        verbose_name = "Mensaje"
        verbose_name_plural = "Mensajes"

    def __str__(self):
        return f"[{self.direction}] {self.body[:50]}"