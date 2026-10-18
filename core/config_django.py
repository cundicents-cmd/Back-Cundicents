# app/django_setup.py
import os
import django
from django.conf import settings


def setup_django():
    """Configura Django la primera vez que se importa este módulo."""
    if not settings.configured:
        settings.configure(
            PASSWORD_HASHERS=[
                "django.contrib.auth.hashers.PBKDF2PasswordHasher",
                "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
                "django.contrib.auth.hashers.Argon2PasswordHasher",
                "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
            ],
            DATABASES={},
            INSTALLED_APPS=[
                "django.contrib.auth",
                "django.contrib.contenttypes",
            ],
            USE_TZ=True,
            SECRET_KEY=os.getenv("DJANGO_SECRET_KEY", "fastapi-integration-secret"),
        )
        django.setup()