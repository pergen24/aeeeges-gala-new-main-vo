from flask import url_for
import io
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from .gmail_service import get_gmail_service

def generate_ticket_pdf(purchase):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    # Datos del ticket
    text = f"""
    Ticket ID: {purchase.id}
    Nombre: {purchase.first_name} {purchase.last_name}
    Email: {purchase.email}
    Tipo de Ticket: {purchase.ticket_type}
    Estado: {purchase.status}
    """

    c.setFont("Helvetica", 12)
    y = 800
    for line in text.strip().split("\n"):
        c.drawString(100, y, line.strip())
        y -= 20

    # Generar QR con URL al ticket (usar dominio de Render con _external=True)
    qr_url = url_for(
        'main.ticket_image',
        ticket_type=purchase.ticket_type,
        _external=True
    )
    qr_img = qrcode.make(qr_url)

    # Guardar QR en BytesIO en formato PNG
    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    qr_reader = ImageReader(qr_buffer)

    # Dibujar QR en PDF
    c.drawImage(qr_reader, 100, 600, 150, 150)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()


def send_ticket_email(purchase, pdf_bytes):
    service = get_gmail_service()

    # Crear mensaje multipart
    message = MIMEMultipart()
    message['to'] = purchase.email
    message['subject'] = "Tu Ticket - Gala Event"
    message.attach(MIMEText(
        f"Hola {purchase.first_name},\n\n"
        f"Tu ticket ({purchase.ticket_type}) ha sido aprobado.\n"
        "Adjunto encontrarás el PDF con tu código QR.\n\n¡Gracias!",
        'plain'
    ))

    # Adjuntar PDF
    part = MIMEApplication(pdf_bytes, Name=f"ticket_{purchase.id}.pdf")
    part['Content-Disposition'] = f'attachment; filename="ticket_{purchase.id}.pdf"'
    message.attach(part)

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    try:
        sent_msg = service.users().messages().send(userId='me', body={'raw': raw}).execute()
        print(f"Correo enviado: ID {sent_msg['id']}")
    except Exception as e:
        print("Ocurrió un error al enviar el ticket:", e)
