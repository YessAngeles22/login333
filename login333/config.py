import os
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret_key'
    FIREBASE_CONFIG='C:\CRED\omar-e61f4-firebase-adminsdk-v27x0-a73b3fe1e5.json'
