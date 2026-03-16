"""
Servicio de WhatsApp para DailyOps
Guarda cada mensaje en BD para el historial del sistema.

Configuración en settings.py:

    # Twilio (sandbox):
    WHATSAPP_PROVIDER  = 'twilio'
    WHATSAPP_FROM      = 'whatsapp:+14155238886'
    TWILIO_ACCOUNT_SID = 'ACxxxxxxxx'
    TWILIO_AUTH_TOKEN  = 'xxxxxxxx'

    # Meta (producción):
    WHATSAPP_PROVIDER = 'meta'
    META_TOKEN        = 'EAAxxxxxxxx'
    META_PHONE_ID     = '1234567890'
"""

import requests
from django.conf import settings


def _limpiar_numero(numero: str) -> str:
    """Normaliza el número: quita espacios/guiones y agrega + si falta."""
    n = numero.strip().replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    if not n.startswith('+'):
        n = '+' + n
    return n


def enviar_whatsapp(numero: str, mensaje: str,
                    inscrito=None, tipo: str = 'manual') -> dict:
    """
    Envía un mensaje de WhatsApp y guarda el registro en BD.

    Parámetros:
        numero   — teléfono destino (con o sin +, con código de país)
        mensaje  — texto a enviar
        inscrito — instancia de Inscrito (opcional, para vincular en historial)
        tipo     — 'registro' | 'asistencia' | 'manual'
    """
    from .models import MensajeWhatsApp

    numero_limpio = _limpiar_numero(numero)
    proveedor     = getattr(settings, 'WHATSAPP_PROVIDER', 'twilio')

    # Crear registro pendiente
    registro = MensajeWhatsApp.objects.create(
        inscrito  = inscrito,
        numero    = numero_limpio,
        mensaje   = mensaje,
        tipo      = tipo,
        estado    = 'pendiente',
    )

    # Enviar según proveedor
    if proveedor == 'twilio':
        resultado = _enviar_twilio(numero_limpio, mensaje)
    elif proveedor == 'meta':
        resultado = _enviar_meta(numero_limpio, mensaje)
    else:
        resultado = {"ok": False, "error": f"Proveedor '{proveedor}' no reconocido"}

    # Actualizar registro con resultado
    if resultado["ok"]:
        registro.estado = 'enviado'
        registro.sid    = resultado.get("sid") or resultado.get("id", "")
    else:
        registro.estado    = 'error'
        registro.error_msg = resultado.get("error", "Error desconocido")

    registro.save(update_fields=['estado', 'sid', 'error_msg'])
    return resultado


# ── TWILIO ────────────────────────────────────────────────

def _enviar_twilio(numero: str, mensaje: str) -> dict:
    try:
        sid   = settings.TWILIO_ACCOUNT_SID
        token = settings.TWILIO_AUTH_TOKEN
        desde = settings.WHATSAPP_FROM
    except AttributeError as e:
        return {"ok": False, "error": f"Falta config Twilio: {e}"}

    url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"

    try:
        resp = requests.post(
            url,
            data={"From": desde, "To": f"whatsapp:{numero}", "Body": mensaje},
            auth=(sid, token),
            timeout=10,
        )
        data = resp.json()
        if resp.status_code in (200, 201):
            print(f"[WA Twilio] ✓ {numero} — {data.get('sid')}")
            return {"ok": True, "sid": data.get("sid")}
        else:
            error = data.get("message", str(data))
            print(f"[WA Twilio] ✗ {error}")
            return {"ok": False, "error": error}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ── META ──────────────────────────────────────────────────

def _enviar_meta(numero: str, mensaje: str) -> dict:
    try:
        token    = settings.META_TOKEN
        phone_id = settings.META_PHONE_ID
    except AttributeError as e:
        return {"ok": False, "error": f"Falta config Meta: {e}"}

    url = f"https://graph.facebook.com/v19.0/{phone_id}/messages"

    try:
        resp = requests.post(
            url,
            json={
                "messaging_product": "whatsapp",
                "to":   numero,
                "type": "text",
                "text": {"body": mensaje},
            },
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type":  "application/json",
            },
            timeout=10,
        )
        data = resp.json()
        if resp.status_code == 200:
            msg_id = data.get("messages", [{}])[0].get("id", "")
            print(f"[WA Meta] ✓ {numero} — {msg_id}")
            return {"ok": True, "id": msg_id}
        else:
            error = data.get("error", {}).get("message", str(data))
            print(f"[WA Meta] ✗ {error}")
            return {"ok": False, "error": error}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ── MENSAJES PREDEFINIDOS ─────────────────────────────────

def mensaje_registro(inscrito) -> str:
    return (
        f"✅ *Registro confirmado*\n\n"
        f"Hola {inscrito.nombre}, tu inscripción ha sido registrada.\n\n"
        f"📋 *Tus datos:*\n"
        f"• Grado: {inscrito.get_grado_display()}\n"
        f"• Zona: {inscrito.get_zona_display() or '—'}\n"
        f"• Periodo: {inscrito.periodo or '—'}\n"
        f"• Monto: ${inscrito.monto}\n\n"
        f"📱 Tu código QR te llegará por correo electrónico."
    )


def mensaje_asistencia(inscrito, hora: str) -> str:
    return (
        f"✅ *Asistencia registrada*\n\n"
        f"Hola {inscrito.nombre}, tu asistencia fue registrada.\n\n"
        f"🕐 Hora de entrada: *{hora}*\n\n"
        f"¡Gracias por tu puntualidad!"
    )