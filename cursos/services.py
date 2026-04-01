from django.core.mail import EmailMultiAlternatives
from django.conf import settings


def enviar_correo_registro(inscrito):
    """
    Envía correo de confirmación al inscrito con su QR adjunto.
    Se llama desde views.py al crear un nuevo inscrito.
    """

    if not inscrito.correo_electronico:
        print(f"[Correo] {inscrito.nombre} no tiene correo, se omite.")
        return

    asunto = f"Confirmación de inscripción — {inscrito.nombre}"

    # ── Cuerpo en texto plano ──
    texto_plano = f"""
Hola {inscrito.nombre},

Tu inscripción ha sido registrada correctamente.

Datos de tu registro:
  • Nombre:  {inscrito.nombre}
  • Teléfono:   {inscrito.telefono}

Adjunto encontrarás tu código QR personal.
Preséntalo al momento de pasar lista.

Saludos,
{settings.DEFAULT_FROM_EMAIL}
""".strip()

    # ── Cuerpo en HTML ──
    html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0; padding:0; background:#f8fafc; font-family:'Segoe UI',sans-serif;">

  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f8fafc; padding:32px 16px;">
    <tr>
      <td align="center">
        <table width="560" cellpadding="0" cellspacing="0"
               style="background:white; border-radius:16px; overflow:hidden;
                      border:1px solid #e8edf2; max-width:560px; width:100%;">

          <!-- Header con color primario -->
          <tr>
            <td style="background:#303854; padding:28px 32px; text-align:center;">
              <h1 style="color:white; margin:0; font-size:22px; font-weight:700; letter-spacing:-.02em;">
                Confirmación de Inscripción
              </h1>
            </td>
          </tr>

          <!-- Saludo -->
          <tr>
            <td style="padding:28px 32px 0;">
              <p style="font-size:16px; color:#1e293b; margin:0 0 6px; font-weight:600;">
                Hola, {inscrito.nombre} 👋
              </p>
              <p style="font-size:14px; color:#64748b; margin:0; line-height:1.6;">
                Tu inscripción ha sido registrada correctamente.
                Adjunto encontrarás tu código QR personal — preséntalo al momento de pasar lista.
              </p>
            </td>
          </tr>

          <!-- Datos del registro -->
          <tr>
            <td style="padding:24px 32px;">
              <table width="100%" cellpadding="0" cellspacing="0"
                     style="background:#f8fafc; border-radius:12px; border:1px solid #f1f5f9; overflow:hidden;">
                <tr>
                  <td style="padding:14px 20px; border-bottom:1px solid #f1f5f9;">
                    <span style="font-size:11px; font-weight:600; color:#94a3b8; text-transform:uppercase; letter-spacing:.06em;">Nombre</span><br>
                    <span style="font-size:15px; font-weight:600; color:#1e293b;">{inscrito.nombre}</span>
                  </td>
                </tr>
                <tr>
                  <td style="padding:14px 20px; border-bottom:1px solid #f1f5f9;">
                    <span style="font-size:11px; font-weight:600; color:#94a3b8; text-transform:uppercase; letter-spacing:.06em;">Teléfono</span><br>
                    <span style="font-size:14px; color:#475569;">{inscrito.telefono or '—'}</span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- QR inline si existe -->
          {'<tr><td style="padding:0 32px 24px; text-align:center;"><p style="font-size:13px; color:#94a3b8; margin:0 0 12px;">Tu código QR personal</p><img src="cid:qr_image" alt="QR" style="width:180px; height:180px; border-radius:12px;"></td></tr>' if inscrito.qr_image else ''}

          <!-- Footer -->
          <tr>
            <td style="padding:20px 32px; background:#f8fafc; border-top:1px solid #f1f5f9;
                       text-align:center;">
              <p style="font-size:12px; color:#94a3b8; margin:0; line-height:1.6;">
                Este es un correo automático, por favor no respondas a este mensaje.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>

</body>
</html>
""".strip()

    # ── Construir y enviar ──
    email = EmailMultiAlternatives(
        subject=asunto,
        body=texto_plano,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[inscrito.correo_electronico],
    )
    email.attach_alternative(html, "text/html")

    # Adjuntar QR como archivo
    if inscrito.qr_image:
        try:
            inscrito.qr_image.open('rb')
            qr_content = inscrito.qr_image.read()
            inscrito.qr_image.close()

            # Adjunto descargable
            email.attach(
                filename=f"QR_{inscrito.nombre}.png",
                content=qr_content,
                mimetype="image/png",
            )

            # Imagen inline (cid)
            from email.mime.image import MIMEImage
            img_mime = MIMEImage(qr_content)
            img_mime.add_header('Content-ID', '<qr_image>')
            img_mime.add_header('Content-Disposition', 'inline', filename='qr.png')
            email.attach(img_mime)

        except Exception as e:
            print(f"[Correo] No se pudo adjuntar QR: {e}")

    email.send(fail_silently=False)
    print(f"[Correo] Enviado a {inscrito.correo_electronico}")