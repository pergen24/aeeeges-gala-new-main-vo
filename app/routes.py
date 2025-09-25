import os
from flask import Blueprint, current_app, render_template, request, redirect, url_for, send_file, flash
from werkzeug.utils import secure_filename
from . import db, mail
from .models import TicketPurchase
from .utils import generate_ticket_pdf, send_ticket_email
from .auth import admin_required
import re
import dns.resolver
from flask_mail import Message
from .gmail_service import send_email
#from werkzeug.security import generate_password_hash, check_password_hash




bp = Blueprint('main', __name__)

ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

# RUTAS CLIENTE
@bp.route('/')
def index():
    return render_template('cliente/index.html')

@bp.route('/elegir')
def elegir_ticket():
    ticket_types = [
        {"name": "GENERAL 5000", "image": "images/tickets/estandar.jpg"},
#        {"name": "VIP", "image": "images/tickets/vip.jpg"},
        {"name": "CON CARNET DE LA AEEEGS 4000", "image": "/images/tickets/especial.jpg"}
    ]
    return render_template('cliente/elegir_ticket.html', ticket_types=ticket_types)


@bp.route('/ticket_image/<ticket_type>')
def ticket_image(ticket_type):
    images = {
        "GENERAL 5000": "images/tickets/estandar.jpg",
#        "VIP": "images/tickets/vip.jpg",
        "CON CARNET DE LA AEEEGS 4000": "images/tickets/especial.jpg"
    }
    img_path = images.get(ticket_type.upper())
    if not img_path:
        return "Tipo de ticket no encontrado", 404
    return render_template('cliente/ticket_image.html', ticket_type=ticket_type, img_path=img_path)



#@bp.route('/ticket_image/<ticket_type>')
#def ticket_image(ticket_type):
    # Diccionario de imágenes por tipo de ticket
#    images = {
#        "GENERAL": "images/tickets/estandar.jpg",
#        "VIP": "images/tickets/vip.jpg",
#        "INVITADO ESPECIAL": "images/tickets/especial.jpg"
#    }

#    img_path = images.get(ticket_type.upper())
#    if not img_path:
#        return "Tipo de ticket no encontrado", 404

#    return render_template('cliente/ticket_image.html', ticket_type=ticket_type, img_path=img_path)


# Regex simple para validar estructura del email
#EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")

#def is_valid_email(email):
#    """Valida formato y dominio """
#    if not EMAIL_REGEX.match(email):
#        return False

#    try:
#        domain = email.split("@")[1]
        # verificar que el dominio tenga registros MX
#        dns.resolver.resolve(domain, "MX")
#        return True
#    except Exception:
#        return False

#import re
#import dns.resolver

# Regex simple para validar estructura del email
EMAIL_REGEX = re.compile(r"^[\w\.\+-]+@[\w\.-]+\.\w+$")

def is_valid_email(email):
    """Valida formato y dominio del correo"""
    if not EMAIL_REGEX.match(email):
        return False

    try:
        domain = email.split("@")[1]
        # Verificar que el dominio tenga registros MX
        dns.resolver.resolve(domain, "MX")
        return True
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout):
        return False



@bp.route('/checkout/<ticket_type>', methods=['GET', 'POST'])
def checkout(ticket_type):
    if request.method == 'POST':
        # recoger datos
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        address = request.form.get('address')
        city = request.form.get('city')
        phone = request.form.get('phone')

        # ✅ validar email antes de guardar
        if not is_valid_email(email):
            flash("❌ El correo electrónico no es válido o el dominio no existe.", "danger")
            return render_template('cliente/checkout.html', ticket_type=ticket_type,
                                   first_name=first_name, last_name=last_name,
                                   email=email, address=address, city=city, phone=phone)

        # Guardar si todo va bien
        purchase = TicketPurchase(
            ticket_type=ticket_type,
            first_name=first_name,
            last_name=last_name,
            email=email,
            address=address,
            city=city,
            phone=phone,
            status='pending'
        )
        db.session.add(purchase)
        db.session.commit()

        # redirigir a página para que suba su recibo
        return redirect(url_for('.subir_recibo', purchase_id=purchase.id))

    return render_template('cliente/checkout.html', ticket_type=ticket_type)




#@bp.route('/subir_recibo/<int:purchase_id>', methods=['GET', 'POST'])
#def subir_recibo(purchase_id):
#    purchase = TicketPurchase.query.get_or_404(purchase_id)
#    if request.method == 'POST':
#        if 'receipt' not in request.files:
#            flash('No file part')
#            return redirect(request.url)
#        file = request.files['receipt']
#        if file and allowed_file(file.filename):
#            filename = secure_filename(f"{purchase.id}_{file.filename}")
#            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
#            file.save(save_path)
#            purchase.receipt_filename = filename
#            purchase.status = 'uploaded'
#            db.session.commit()
#            return redirect(url_for('.gracias'))
#        else:
#            flash('Archivo no permitido')
#            return redirect(request.url)
#    return render_template('cliente/subir_recibo.html', purchase=purchase)

@bp.route('/subir_recibo/<int:purchase_id>', methods=['GET', 'POST'])
def subir_recibo(purchase_id):
    purchase = TicketPurchase.query.get_or_404(purchase_id)

    if request.method == 'POST':
        files = []
        for field in ['receipt1', 'receipt2']:
            file = request.files.get(field)
            if file and allowed_file(file.filename):
                filename = secure_filename(f"{purchase.id}_{field}_{file.filename}")
                save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(save_path)
                files.append(filename)
            elif file:
                flash(f"Archivo {field} no permitido")
                return redirect(request.url)

        # Guardar los nombres en la base de datos
        if files:
            purchase.receipt_filename1 = files[0] if len(files) > 0 else None
            purchase.receipt_filename2 = files[1] if len(files) > 1 else None
            purchase.status = 'uploaded'
            db.session.commit()
            return redirect(url_for('.gracias'))
        else:
            flash("Debes subir al menos un recibo")
            return redirect(request.url)

    return render_template('cliente/subir_recibo.html', purchase=purchase)


@bp.route('/gracias')
def gracias():
    return render_template('cliente/gracias.html')

# RUTAS ADMIN (simple, sin auth para demo)
@bp.route('/admin')
@admin_required
def admin_index():
    purchases = TicketPurchase.query.order_by(TicketPurchase.created_at.desc()).all()
    return render_template('admin/index.html', purchases=purchases)

@bp.route('/admin/recibos')
@admin_required
def admin_recibos():
    purchases = TicketPurchase.query.filter(TicketPurchase.status.in_(['uploaded','pending'])).all()
    return render_template('admin/recibos.html', purchases=purchases)

#@bp.route('/admin/approve/<int:purchase_id>', methods=['POST'])
#def admin_approve(purchase_id):
#    purchase = TicketPurchase.query.get_or_404(purchase_id)
    # marcar aprobado
#    purchase.status = 'approved'
#    db.session.commit()

    # generar PDF con QR y devolverlo al admin (descarga)
#    pdf_bytes = generate_pdf_with_qr(purchase.to_dict())
#    filename = f"ticket_{purchase.id}.pdf"
#    return send_file(
#        io.BytesIO(pdf_bytes),
##        download_name=filename,
#        as_attachment=True,
#        mimetype='application/pdf'
#    )

@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    # servir recibos (solo demo)
    return send_file(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))




#from flask import current_app, flash, redirect, url_for
#from .models import TicketPurchase, db
#from .utils import generate_ticket_pdf
#from .gmail_service import send_email  # <-- tu función que usa Gmail API
#import os



@bp.route('/admin/approve/<int:purchase_id>', methods=['POST'])
def admin_approve(purchase_id):
    purchase = TicketPurchase.query.get_or_404(purchase_id)

    # Marcar como aprobado
    purchase.status = 'approved'
    db.session.commit()

    try:
        # Generar PDF con QR
        pdf_bytes = generate_ticket_pdf(purchase)

        # Guardar PDF en el servidor
        tickets_folder = current_app.config.get('GENERATED_TICKETS_FOLDER', '/app/generated_tickets')
        os.makedirs(tickets_folder, exist_ok=True)
        pdf_filename = f"ticket_{purchase.id}.pdf"
        pdf_path = os.path.join(tickets_folder, pdf_filename)
        with open(pdf_path, 'wb') as f:
            f.write(pdf_bytes)

        # Guardar nombre del archivo en la compra (opcional)
        purchase.pdf_filename = pdf_filename
        db.session.commit()

        # Enviar email al usuario con Gmail API
        subject = f"Tu Ticket #{purchase.id} - Gala Event"
        body = f"""
Hola {purchase.first_name},

Tu ticket ({purchase.ticket_type}) ha sido aprobado.
Adjunto encontrarás el PDF con tu código QR.

¡Gracias!
"""
        # Usando la nueva versión de send_email con attachments
        send_email(
            to=purchase.email,
            subject=subject,
            body=body,
            attachments=[{'filename': pdf_filename, 'content_bytes': pdf_bytes}]
        )

        flash(f"Ticket #{purchase.id} aprobado, enviado por email y guardado en el servidor.", "success")

    except Exception as e:
        flash(f"Error al generar/enviar/guardar el ticket: {str(e)}", "danger")

    return redirect(url_for("main.admin_index"))




#@bp.route('/admin/approve/<int:purchase_id>', methods=['POST'])
#def admin_approve(purchase_id):
#    purchase = TicketPurchase.query.get_or_404(purchase_id)

    # Marcar como aprobado
#    purchase.status = 'approved'
#    db.session.commit()

#    try:
        # Generar PDF con QR
#        pdf_bytes = generate_ticket_pdf(purchase)

        # Guardar PDF en el servidor
#        tickets_folder = current_app.config.get('GENERATED_TICKETS_FOLDER', '/app/generated_tickets')
#        os.makedirs(tickets_folder, exist_ok=True)
#        pdf_filename = f"ticket_{purchase.id}.pdf"
#        pdf_path = os.path.join(tickets_folder, pdf_filename)
#        with open(pdf_path, 'wb') as f:
#            f.write(pdf_bytes)

        # Guardar nombre del archivo en la compra (opcional)
#        purchase.pdf_filename = pdf_filename
#        db.session.commit()

        # Enviar email al usuario con el PDF adjunto
#        send_ticket_email(purchase, pdf_bytes)

#        flash(f"Ticket #{purchase.id} aprobado, enviado por email y guardado en el servidor.", "success")

#    except Exception as e:
#        flash(f"Error al generar/enviar/guardar el ticket: {str(e)}", "danger")

#    return redirect(url_for("main.admin_index"))







#@bp.route('/admin/suspend/<int:purchase_id>', methods=['POST'])
#@admin_required
#def admin_suspend(purchase_id):
#    purchase = TicketPurchase.query.get_or_404(purchase_id)#

#    try:
        # Eliminar recibos del servidor si existen
#        for receipt in [purchase.receipt_filename1, purchase.receipt_filename2]:
#            if receipt:
#                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], receipt)
#                if os.path.exists(file_path):
#                    os.remove(file_path)

        # Si ya tenía un PDF generado, también lo borramos
#        if purchase.pdf_filename:
#            tickets_folder = current_app.config.get('GENERATED_TICKETS_FOLDER', '/app/generated_tickets')
#            pdf_path = os.path.join(tickets_folder, purchase.pdf_filename)
#            if os.path.exists(pdf_path):
#                os.remove(pdf_path)

        # Eliminar el registro de la compra
#        db.session.delete(purchase)
#        db.session.commit()

#        flash(f"Compra #{purchase.id} suspendida y eliminada del sistema.", "warning")

#    except Exception as e:
#        flash(f"Error al suspender la compra: {str(e)}", "danger")

#    return redirect(url_for("main.admin_index"))



@bp.route('/admin/suspend/<int:purchase_id>', methods=['POST'])
@admin_required
def admin_suspend(purchase_id):
    purchase = TicketPurchase.query.get_or_404(purchase_id)

    # Borrar recibos físicos del servidor si existen
    for field in ["receipt_filename1", "receipt_filename2"]:
        filename = getattr(purchase, field, None)
        if filename:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    current_app.logger.warning(f"No se pudo borrar {file_path}: {e}")

    # Enviar correo de notificación usando Gmail API
    try:
        subject = "Solicitud de Ticket Denegada - Gala Event"
        body = f"""Hola {purchase.first_name},

Lamentamos informarte que tu solicitud para el ticket ({purchase.ticket_type}) 
ha sido denegada por el administrador.

Si crees que se trata de un error, por favor contacta con el equipo de soporte:
visionalfa29@gmail.com
+221 77 554 20 15
+221 78 103 70 64
+221 77 175 53 52

Atentamente,
VISION ALFA
"""
        # Llamada a la función unificada de send_email
        send_email(
            to=purchase.email,
            subject=subject,
            body=body,
            attachments=[]  # No hay adjuntos en este caso
        )
    except Exception as e:
        current_app.logger.error(f"Error al enviar correo de suspensión: {e}")

    # Eliminar la compra de la base de datos
    db.session.delete(purchase)
    db.session.commit()

    flash(f"El recibo #{purchase.id} fue suspendido, eliminado y el usuario notificado.", "danger")
    return redirect(url_for("main.admin_index"))

