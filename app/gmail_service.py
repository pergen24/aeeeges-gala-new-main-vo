# gmail_service.py
import os
import base64
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from app.config import Config

def get_gmail_service():
    creds = None
    # Si ya existe token.json, lo cargamos
    if os.path.exists(Config.TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(Config.TOKEN_FILE, Config.SCOPES)
    # Si no, generamos un token nuevo
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(Config.CLIENT_SECRET_FILE, Config.SCOPES)
            creds = flow.run_local_server(port=0)
        with open(Config.TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def send_email(to, subject, body, attachments=None):
    """
    Envía un correo usando Gmail API.
    
    :param to: Destinatario (string)
    :param subject: Asunto del correo
    :param body: Cuerpo del correo (texto)
    :param attachments: Lista de diccionarios con 'filename' y 'content_bytes' opcional
    """
    service = get_gmail_service()

    # Construir mensaje multipart si hay adjuntos
    if attachments:
        msg = MIMEMultipart()
        msg.attach(MIMEText(body, 'plain'))
    else:
        msg = MIMEText(body, 'plain')

    msg['to'] = to
    msg['subject'] = subject

    # Agregar adjuntos si los hay
    if attachments:
        for attach in attachments:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attach['content_bytes'])
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{attach["filename"]}"')
            msg.attach(part)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    try:
        message = service.users().messages().send(userId='me', body={'raw': raw}).execute()
        print('Correo enviado: ID {}'.format(message['id']))
    except HttpError as error:
        print('Ocurrió un error:', error)
