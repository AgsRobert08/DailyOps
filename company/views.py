from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Company
from company.models import User  # ajusta según tu app


# ── AUTH ────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect("company:dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("company:dashboard")
        else:
            messages.error(request, "Usuario o contraseña incorrectos")

    return render(request, "auth/login.html")


def logout_view(request):
    logout(request)
    return redirect("company:login")


# ── DASHBOARD ───────────────────────────────────────────

@login_required
def dashboard(request):
    context = {
        "total_users":  User.objects.count(),
        "active_users": User.objects.filter(is_active=True).count(),
        "admin_users":  User.objects.filter(is_superuser=True).count(),
    }
    return render(request, "dashboard/index.html", context)


# ── COMPANY ─────────────────────────────────────────────

@login_required
def company_settings(request):
    company, _ = Company.objects.get_or_create(
        pk=1,
        defaults={"name": "Mi Empresa"}
    )

    if request.method == "POST":
        # Identidad
        company.name   = request.POST.get("name", "")
        company.slogan = request.POST.get("slogan", "")

        # Colores
        company.primary_color    = request.POST.get("primary_color",    "#303854")
        company.secondary_color  = request.POST.get("secondary_color",  "#C2CDD5")
        company.background_color = request.POST.get("background_color", "#F6F3EA")

        # Contacto
        company.phone    = request.POST.get("phone",    "")
        company.email    = request.POST.get("email",    "")
        company.address  = request.POST.get("address",  "")
        company.website  = request.POST.get("website",  "")
        company.whatsapp = request.POST.get("whatsapp", "")

        # Redes sociales
        company.facebook  = request.POST.get("facebook",  "")
        company.instagram = request.POST.get("instagram", "")
        company.tiktok    = request.POST.get("tiktok",    "")

        # Logos
        if "logo" in request.FILES:
            company.logo = request.FILES["logo"]
        if "logo_small" in request.FILES:
            company.logo_small = request.FILES["logo_small"]

        company.save()
        messages.success(request, "Configuración guardada correctamente")
        return redirect("company:company_settings")

    return render(request, "company/settings.html", {"company": company})

# ── USERS ───────────────────────────────────────────────

@login_required
def users_list(request):
    users = User.objects.all().order_by("first_name", "username")
    return render(request, "users/list.html", {"users": users})


@login_required
def user_create(request):
    if request.method == "POST":
        username   = request.POST.get("username")
        password   = request.POST.get("password")
        first_name = request.POST.get("first_name", "")
        last_name  = request.POST.get("last_name", "")
        email      = request.POST.get("email", "")
        phone      = request.POST.get("phone", "")
        is_active     = bool(request.POST.get("is_active"))
        is_superuser  = bool(request.POST.get("is_superuser"))
        is_operador   = bool(request.POST.get("is_operador"))

        if User.objects.filter(username=username).exists():
            messages.error(request, f'El usuario "{username}" ya existe')
        else:
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email,
            )
            user.phone       = phone
            user.is_active   = is_active
            user.is_superuser = is_superuser
            user.is_operador  = is_operador
            if "profile_photo" in request.FILES:
                user.profile_photo = request.FILES["profile_photo"]
            user.save()
            messages.success(request, f'Usuario "{username}" creado correctamente')
            return redirect("company:users_list")

    return render(request, "users/form.html", {"editing": False})


@login_required
def user_edit(request, pk):
    edit_user = get_object_or_404(User, pk=pk)

    if request.method == "POST":
        edit_user.username   = request.POST.get("username", edit_user.username)
        edit_user.first_name = request.POST.get("first_name", "")
        edit_user.last_name  = request.POST.get("last_name", "")
        edit_user.email      = request.POST.get("email", "")
        edit_user.phone      = request.POST.get("phone", "")
        edit_user.is_active     = bool(request.POST.get("is_active"))
        edit_user.is_superuser  = bool(request.POST.get("is_superuser"))
        edit_user.is_operador   = bool(request.POST.get("is_operador"))
        password = request.POST.get("password")
        if password:
            edit_user.set_password(password)

        if "profile_photo" in request.FILES:
            edit_user.profile_photo = request.FILES["profile_photo"]

        edit_user.save()
        messages.success(request, "Usuario actualizado correctamente")
        return redirect("company:users_list")

    return render(request, "users/form.html", {
        "editing": True,
        "edit_user": edit_user,
    })


@login_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        username = user.username
        user.delete()
        messages.success(request, f'Usuario "{username}" eliminado')
    return redirect("company:users_list")
import os
import json
import datetime

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import google.auth.transport.requests

from .models import GoogleCalendarToken

# ── NECESARIO PARA DESARROLLO LOCAL (http) ──────────────
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


def get_flow(state=None):
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id":     settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                "auth_uri":      "https://accounts.google.com/o/oauth2/auth",
                "token_uri":     "https://oauth2.googleapis.com/token",
            }
        },
        scopes=["https://www.googleapis.com/auth/calendar"],
        state=state,
    )
    flow.code_verifier = None  # ← desactiva PKCE
    return flow


from urllib.parse import urlparse, urlencode, parse_qs, urlunparse

@login_required
def calendar_connect(request):
    flow = get_flow()
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI

    auth_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent",
    )

    # ← Eliminar code_challenge y code_challenge_method de la URL
    parsed = urlparse(auth_url)
    params = parse_qs(parsed.query, keep_blank_values=True)
    params.pop("code_challenge", None)
    params.pop("code_challenge_method", None)
    
    # Reconstruir URL limpia
    clean_query = urlencode({k: v[0] for k, v in params.items()})
    clean_url   = urlunparse(parsed._replace(query=clean_query))

    request.session["oauth_state"] = state
    request.session["code_verifier"] = None  # limpiar verifier
    request.session.modified = True

    print("CLEAN URL:", clean_url)  # verifica que ya no tenga code_challenge
    return redirect(clean_url)

def calendar_callback(request):
    if not request.user.is_authenticated:
        return redirect("company:login")

    try:
        state = request.session.get("oauth_state")
        flow  = get_flow(state=state)
        flow.redirect_uri  = settings.GOOGLE_REDIRECT_URI
        flow.code_verifier = ""  # ← vacío, no None

        flow.fetch_token(authorization_response=request.build_absolute_uri())
        creds = flow.credentials

        GoogleCalendarToken.objects.update_or_create(
            user=request.user,
            defaults={
                "access_token":  creds.token,
                "refresh_token": creds.refresh_token,
                "token_expiry":  creds.expiry,
            }
        )
        messages.success(request, "✅ Google Calendar conectado correctamente.")
        return redirect("company:calendar_view")

    except Exception as e:
        messages.error(request, f"Error al conectar Google Calendar: {str(e)}")
        return redirect("company:dashboard")

@login_required
def calendar_disconnect(request):
    GoogleCalendarToken.objects.filter(user=request.user).delete()
    messages.success(request, "Google Calendar desconectado.")
    return redirect("company:calendar_view")


@csrf_exempt
def calendar_webhook(request):
    if request.method != "POST":
        return HttpResponse(status=405)
    resource_state = request.headers.get("X-Goog-Resource-State")
    channel_id     = request.headers.get("X-Goog-Channel-ID")
    if resource_state == "sync":
        return HttpResponse(status=200)
    print(f"📅 Cambio detectado en canal: {channel_id}")
    return HttpResponse(status=200)


@login_required
def calendar_view(request):
    try:
        GoogleCalendarToken.objects.get(user=request.user)
    except GoogleCalendarToken.DoesNotExist:
        return redirect("company:calendar_connect")
    return render(request, "company/calendar.html")

@login_required
def calendar_events_api(request):
    try:
        token = GoogleCalendarToken.objects.get(user=request.user)
        creds = token.to_credentials()

        if creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
            token.access_token = creds.token
            token.token_expiry = creds.expiry
            token.save()

        service = build("calendar", "v3", credentials=creds)

        # ← DEBUG TEMPORAL: ver todos los calendarios
        calendars = service.calendarList().list().execute()
        print(">>> CALENDARIOS DISPONIBLES:")
        for c in calendars.get("items", []):
            print(f"   - {c.get('summary')} | {c.get('id')} | primary={c.get('primary')}")

        # ← DEBUG TEMPORAL: buscar eventos en TODOS los calendarios
        from datetime import timezone
        time_min_raw = request.GET.get("start")
        time_max_raw = request.GET.get("end")

        if time_min_raw:
            time_min = datetime.datetime.fromisoformat(time_min_raw).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            time_min = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        if time_max_raw:
            time_max = datetime.datetime.fromisoformat(time_max_raw).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            time_max = None

        print(">>> FECHAS:", time_min, "→", time_max)

        all_events = []
        for cal in calendars.get("items", []):
            cal_id = cal.get("id")
            try:
                params = {
                    "calendarId":   cal_id,
                    "timeMin":      time_min,
                    "singleEvents": True,
                    "orderBy":      "startTime",
                    "maxResults":   250,
                }
                if time_max:
                    params["timeMax"] = time_max

                result = service.events().list(**params).execute()
                items  = result.get("items", [])
                print(f"   → {cal.get('summary')}: {len(items)} eventos")
                all_events.extend(items)
            except Exception as cal_error:
                print(f"   → ERROR en {cal.get('summary')}: {cal_error}")

        print(f">>> TOTAL EVENTOS: {len(all_events)}")

        formatted = []
        for e in all_events:
            start = e.get("start", {})
            end   = e.get("end",   {})
            formatted.append({
                "id":          e.get("id"),
                "title":       e.get("summary", "Sin título"),
                "start":       start.get("dateTime", start.get("date")),
                "end":         end.get("dateTime",   end.get("date")),
                "description": e.get("description", ""),
                "location":    e.get("location",    ""),
                "allDay":      "date" in start,
                "color":       "#303854",
            })

        return JsonResponse({"events": formatted})

    except GoogleCalendarToken.DoesNotExist:
        return JsonResponse({"error": "No conectado"}, status=401)
    except Exception as e:
        print(">>> ERROR:", str(e))
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)
    
@login_required
def calendar_event_create(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    data    = json.loads(request.body)
    token   = GoogleCalendarToken.objects.get(user=request.user)
    creds   = token.to_credentials()
    service = build("calendar", "v3", credentials=creds)

    created = service.events().insert(
        calendarId="primary",
        body={
            "summary":     data.get("title", "Nuevo evento"),
            "description": data.get("description", ""),
            "location":    data.get("location", ""),
            "start": {"dateTime": data["start"], "timeZone": "America/Mexico_City"},
            "end":   {"dateTime": data["end"],   "timeZone": "America/Mexico_City"},
        }
    ).execute()
    return JsonResponse({"id": created["id"], "status": "created"})


@login_required
def calendar_event_update(request, event_id):
    if request.method != "PUT":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    data    = json.loads(request.body)
    token   = GoogleCalendarToken.objects.get(user=request.user)
    creds   = token.to_credentials()
    service = build("calendar", "v3", credentials=creds)

    updated = service.events().update(
        calendarId="primary",
        eventId=event_id,
        body={
            "summary":     data.get("title", ""),
            "description": data.get("description", ""),
            "location":    data.get("location", ""),
            "start": {"dateTime": data["start"], "timeZone": "America/Mexico_City"},
            "end":   {"dateTime": data["end"],   "timeZone": "America/Mexico_City"},
        }
    ).execute()
    return JsonResponse({"id": updated["id"], "status": "updated"})


@login_required
def calendar_event_delete(request, event_id):
    if request.method != "DELETE":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    token   = GoogleCalendarToken.objects.get(user=request.user)
    creds   = token.to_credentials()
    service = build("calendar", "v3", credentials=creds)
    service.events().delete(calendarId="primary", eventId=event_id).execute()
    return JsonResponse({"status": "deleted"})