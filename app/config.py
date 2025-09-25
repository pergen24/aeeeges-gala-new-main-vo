import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'super-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql+psycopg2://neondb_owner:npg_mUPGMj0O5eyq@ep-green-boat-adjdm91u-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
    )

    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/app/uploads')
    GENERATED_TICKETS_FOLDER = os.environ.get('GENERATED_TICKETS_FOLDER', '/app/generated_tickets')

    # Gmail API
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'membilambasipergentino@gmail.com')
    MAIL_DEFAULT_SENDER = ("Gala Tickets", MAIL_USERNAME)

    # OAuth
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    CLIENT_SECRET_FILE = os.environ.get(
        'CLIENT_SECRET_FILE',
        '/app/app/client_secret_969853205032-s1s8tlujsdob6ejhusao4oki5oc6i8g2.apps.googleusercontent.com.json'
    )
    TOKEN_FILE = os.environ.get('TOKEN_FILE', '/app/app/token.json')
