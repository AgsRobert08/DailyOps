from django.urls import path
from . import views

app_name = "cursos"

urlpatterns = [
    # Inscripciones
    path("inscripciones/",                   views.inscripciones_list,   name="inscripciones"),
    path("inscripciones/nueva/",             views.inscripcion_create,   name="inscripcion_create"),
    path("inscripciones/pdf/",               views.inscripciones_pdf,    name="inscripciones_pdf"),
    path("inscripciones/<int:pk>/",          views.inscripcion_edit,     name="inscripcion_edit"),
    path("inscripciones/<int:pk>/eliminar/", views.inscripcion_delete,   name="inscripcion_delete"),
    path("inscripciones/<int:pk>/qr/",       views.inscripcion_qr,       name="inscripcion_qr"),

    # Asistencia
    path("asistencia/",                      views.asistencia_list,      name="asistencia"),
    path("asistencia/escanear/",             views.asistencia_scan,      name="asistencia_scan"),
    path("asistencia/registrar/",            views.asistencia_registrar, name="asistencia_registrar"),
    path("asistencia/pdf/",                  views.asistencia_pdf,       name="asistencia_pdf"),
    path("asistencia/<int:pk>/eliminar/",    views.asistencia_delete,    name="asistencia_delete"),

    path("inscripciones/excel/", views.inscripciones_excel, name="inscripciones_excel"),
    path("asistencia/excel/",    views.asistencia_excel,    name="asistencia_excel"),

    # AJAX búsqueda
    path("buscar/",                          views.buscar_inscrito,      name="buscar_inscrito"),
    # WhatsApp
    path("whatsapp/",        views.whatsapp_historial, name="whatsapp_historial"),
    path("whatsapp/enviar/", views.whatsapp_enviar,    name="whatsapp_enviar"),
]