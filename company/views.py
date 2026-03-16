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
        company.name             = request.POST.get("name", "")
        company.phone            = request.POST.get("phone", "")
        company.email            = request.POST.get("email", "")
        company.address          = request.POST.get("address", "")
        company.primary_color    = request.POST.get("primary_color", "#303854")
        company.secondary_color  = request.POST.get("secondary_color", "#C2CDD5")
        company.background_color = request.POST.get("background_color", "#F6F3EA")

        if "logo" in request.FILES:
            company.logo = request.FILES["logo"]

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