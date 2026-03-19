from django.db import models
import uuid
import qrcode
import io
from django.core.files.base import ContentFile


def qr_upload_path(instance, filename):
    return f"qr/inscritos/{instance.codigo}.png"


class Inscrito(models.Model):
    codigo = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nombre = models.CharField(max_length=150, null=True)

    GENEROS = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]
    genero = models.CharField(max_length=2, choices=GENEROS)

    ZONAS = [
        ('CEN', 'CENTRAL'), ('CDMX', 'CD. DE MEX.'), ('PUE', 'PUEBLA, PUE.'),
        ('XAL', 'XALAPA, VER.'), ('MIS', 'MISANTLA, VER.'), ('ALT', 'ALTOTONGA, VER.'),
        ('JUC', 'JUCHIQUE DE FERRER, VER.'), ('POZ', 'POZA RICA, VER.'),
        ('CUE', 'CUERNAVACA, MOR.'), ('URU', 'URUAPAN, MICH.'), ('CAR', 'CARDENAS, TAB.'),
        ('GDL', 'GUADALAJARA, JAL.'), ('SIL', 'SILAO, GTO.'), ('PAC', 'PACHUCA, HGO.'),
        ('CAN', 'CANCÚN, Q. R.'), ('JUA', 'CIUDAD JUÁREZ, CHIH.'),
        ('MAT', 'MATÍAS ROMERO, OAX.'), ('CHP', 'CHILPANCINGO, GRO.'),
        ('TIJ', 'TIJUANA, B.C.'), ('REY', 'REYNOSA, TAMPS.'),
        ('TOL', 'TOLUCA, EDO. DE MEX.'), ('OAX', 'OAXACA, OAX.'),
        ('ELG', 'ELGIN ILLINOIS, EUA'), ('TAP', 'TAPACHULA, CHIS.'),
        ('CAB', 'CABO SAN LUCAS, B.C.S.'), ('TEZ', 'TEZIUTLÁN, PUE.'),
        ('TAM', 'TAMPICO, TAMPS.'), ('VER', 'VERACRUZ, VER.'),
        ('TOP', 'TOPILEJO, CD. MEX.'), ('NEZ', 'CIUDAD NEZAHUALCÓYOTL, EDOMEX'),
        ('MIR', 'MIRAFLORES, EDOMEX'), ('CAL', 'CALPULALPAN, TLAX.'),
        ('COY', 'COYOTEPEC, EDOMEX'), ('CSU', 'CENTRO Y SUDAMÉRICA'),
    ]
    zona    = models.CharField(max_length=100, choices=ZONAS, blank=True, null=True)
    subzona = models.CharField(max_length=100, blank=True, null=True)

    otra_denominacion = models.BooleanField(default=False)
    denominacion      = models.CharField(max_length=150, blank=True, null=True)
    iglesia           = models.CharField(max_length=150, null=True, blank=True)
    pastor            = models.CharField(max_length=150, null=True, blank=True)

    telefono           = models.CharField(max_length=20, unique=True)
    correo_electronico = models.EmailField(null=True, blank=True)

    GRADOS = [
        ('MIN',    'MINISTRO / DIACONISA'),
        ('EG_ESC', 'EGRESADO DEL I.T.E. (Sistema Escolarizado)'),
        ('EG_AB',  'EGRESADO DEL I.T.E. (Sistema Abierto)'),
        ('EST_1E', 'ESTUDIANTE (PRIMER AÑO) S.E.'),
        ('EST_2E', 'ESTUDIANTE (SEGUNDO AÑO) S.E.'),
        ('EST_3E', 'ESTUDIANTE (TERCER AÑO) S.E.'),
        ('EST_1A', 'ESTUDIANTE (PRIMER AÑO) S. ABIERTO'),
        ('EST_2A', 'ESTUDIANTE (SEGUNDO AÑO) S. ABIERTO'),
        ('EST_3A', 'ESTUDIANTE (TERCER AÑO) S. ABIERTO'),
        ('EST_4A', 'ESTUDIANTE (CUARTO AÑO) S. ABIERTO'),
        ('OBR',    'OBRERO LAICO'),
        ('ANC',    'ANCIANO DE IGLESIA'),
        ('OTR',    'OTRO (ESPECIFICAR)'),
        ('REP_Z',  'REPRESENTANTE DE ZONA'),
        ('REP_S',  'REPRESENTANTE DE SUB ZONA'),
        ('EG_XE',  'EGRESADO ITE CAMPUS XALAPA S. ESCOLARIZADO'),
        ('EG_XA',  'EGRESADO ITE CAMPUS XALAPA S. ABIERTO'),
        ('EG_SE',  'EGRESADO ITE CAMPUS SURESTE S. ESCOLARIZADO'),
        ('EG_EL',  'EGRESADO ITE CAMPUS ELGIN, IL'),
        ('SIN_R',  'SIN RANGO'),
    ]
    grado = models.CharField(max_length=100, choices=GRADOS)

    periodo = models.CharField(max_length=50, null=True, blank=True)
    monto   = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    qr_image       = models.ImageField(upload_to=qr_upload_path, blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre or str(self.codigo)

    def generar_qr(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(str(self.codigo))
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        self.qr_image.save(f"{self.codigo}.png", ContentFile(buffer.read()), save=False)

    def save(self, *args, **kwargs):
        es_nuevo = self.pk is None
        super().save(*args, **kwargs)
        if es_nuevo and not self.qr_image:
            self.generar_qr()
            Inscrito.objects.filter(pk=self.pk).update(qr_image=self.qr_image.name)


class Asistencia(models.Model):
    inscrito = models.ForeignKey(
        Inscrito,
        on_delete=models.CASCADE,
        related_name="asistencias"
    )
    fecha   = models.DateField()
    hora    = models.TimeField()
    asistio = models.BooleanField(default=True)

    class Meta:
        unique_together = ('inscrito', 'fecha')
        indexes = [
            models.Index(fields=['fecha']),
            models.Index(fields=['inscrito']),
        ]

    def __str__(self):
        return f"{self.inscrito.nombre} - {self.fecha}"


class MensajeWhatsApp(models.Model):
    """Registro de cada mensaje enviado por WhatsApp."""

    TIPOS = [
        ('registro',   'Registro de inscrito'),
        ('asistencia', 'Confirmación de asistencia'),
        ('manual',     'Mensaje manual'),
    ]

    ESTADOS = [
        ('enviado',  'Enviado'),
        ('error',    'Error'),
        ('pendiente','Pendiente'),
    ]

    inscrito  = models.ForeignKey(
        Inscrito,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="mensajes_whatsapp"
    )
    numero    = models.CharField(max_length=20)
    mensaje   = models.TextField()
    tipo      = models.CharField(max_length=20, choices=TIPOS, default='manual')
    estado    = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    error_msg = models.TextField(blank=True, null=True)
    sid       = models.CharField(max_length=100, blank=True, null=True)  # ID de Twilio o Meta
    enviado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-enviado_en']
        indexes  = [models.Index(fields=['enviado_en'])]

    def __str__(self):
        nombre = self.inscrito.nombre if self.inscrito else self.numero
        return f"{nombre} — {self.get_tipo_display()} — {self.estado}"