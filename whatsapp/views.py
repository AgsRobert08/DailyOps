import json
import logging
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db import transaction

from .models import Contact, Conversation, Message
from .services import send_whatsapp_text

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# VISTAS DE INTERFAZ
# ─────────────────────────────────────────────

def inbox(request):
    """Bandeja principal con lista de conversaciones."""
    conversations = Conversation.objects.select_related("contact").order_by("-last_message_at")
    return render(request, "whatsapp/inbox.html", {"conversations": conversations})


def conversation_detail(request, conversation_id):
    """Vista de una conversación individual con mensajes."""
    conversation = get_object_or_404(
        Conversation.objects.select_related("contact"), id=conversation_id
    )
    messages = conversation.messages.order_by("timestamp")

    # Marcar como leída
    conversation.unread_count = 0
    conversation.save(update_fields=["unread_count"])

    return render(request, "whatsapp/conversation.html", {
        "conversation": conversation,
        "messages": messages,
    })


# ─────────────────────────────────────────────
# API INTERNA (llamada por el frontend JS)
# ─────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["POST"])
def send_message(request, conversation_id):
    """Envía un mensaje desde el panel."""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    data = json.loads(request.body)
    body = data.get("body", "").strip()

    if not body:
        return JsonResponse({"error": "El mensaje no puede estar vacío"}, status=400)

    try:
        result = send_whatsapp_text(to=conversation.contact.phone, message=body)
        ycloud_id = result.get("id", "")
    except Exception as e:
        logger.error(f"Error enviando WhatsApp: {e}")
        return JsonResponse({"error": "No se pudo enviar el mensaje"}, status=500)

    msg = Message.objects.create(
        conversation=conversation,
        ycloud_message_id=ycloud_id,
        direction="outbound",
        body=body,
        status="sent",
        timestamp=timezone.now(),
    )

    conversation.last_message_preview = body[:200]
    conversation.last_message_at = msg.timestamp
    conversation.save(update_fields=["last_message_preview", "last_message_at"])

    return JsonResponse({
        "id": msg.id,
        "body": msg.body,
        "direction": msg.direction,
        "status": msg.status,
        "timestamp": msg.timestamp.strftime("%H:%M"),
    })


@require_http_methods(["GET"])
def poll_messages(request, conversation_id):
    """Polling liviano: devuelve mensajes nuevos después de cierto ID."""
    after_id = int(request.GET.get("after", 0))
    conversation = get_object_or_404(Conversation, id=conversation_id)
    msgs = conversation.messages.filter(id__gt=after_id).order_by("timestamp")

    return JsonResponse({
        "messages": [
            {
                "id": m.id,
                "body": m.body,
                "direction": m.direction,
                "status": m.status,
                "timestamp": m.timestamp.strftime("%H:%M"),
            }
            for m in msgs
        ],
        "unread_count": conversation.unread_count,
    })


# ─────────────────────────────────────────────
# WEBHOOK DE YCLOUD
# ─────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["POST"])
def ycloud_webhook(request):
    """Recibe eventos de yCloud (mensajes entrantes y actualizaciones de estado)."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse(status=400)
    print("YCLOUD PAYLOAD:", json.dumps(data, indent=2))


    event_type = data.get("type", "")
    logger.info(f"yCloud webhook: {event_type}")
    
    if event_type == "whatsapp.inbound_message.received":
        _handle_inbound(data.get("whatsappInboundMessage", {}))  # ← cambiar "payload" por esto

    elif event_type == "whatsapp.message.updated":
        _handle_status_update(data.get("whatsappMessage", {}))   # ← cambiar "payload" por esto

    return JsonResponse({"status": "ok"})


def _handle_inbound(payload: dict):
    """Procesa un mensaje entrante y lo guarda en la BD."""
    from_number = payload.get("from", "")
    text = payload.get("text", {}).get("body", "")
    ycloud_id = payload.get("id", "")
    timestamp_str = payload.get("timestamp")

    if not from_number or not text:
        return

    with transaction.atomic():
        contact, _ = Contact.objects.get_or_create(
            phone=from_number,
            defaults={"name": payload.get("customerProfile", {}).get("name", "")}
        )
        # Actualizar nombre si yCloud lo trae
        profile_name = payload.get("customerProfile", {}).get("name", "")
        if profile_name and not contact.name:
            contact.name = profile_name
            contact.save()

        conversation, _ = Conversation.objects.get_or_create(contact=contact)

        msg_time = timezone.now()
        Message.objects.create(
            conversation=conversation,
            ycloud_message_id=ycloud_id,
            direction="inbound",
            body=text,
            status="delivered",
            timestamp=msg_time,
        )

        conversation.unread_count += 1
        conversation.last_message_preview = text[:200]
        conversation.last_message_at = msg_time
        conversation.status = "open"
        conversation.save()


def _handle_status_update(payload: dict):
    """Actualiza el estado de un mensaje saliente (sent/delivered/read/failed)."""
    ycloud_id = payload.get("id", "")
    new_status = payload.get("status", "")

    STATUS_MAP = {
        "sent": "sent",
        "delivered": "delivered",
        "read": "read",
        "failed": "failed",
    }

    if ycloud_id and new_status in STATUS_MAP:
        Message.objects.filter(ycloud_message_id=ycloud_id).update(status=STATUS_MAP[new_status])