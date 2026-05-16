"""
Django settings for animalsite project.
"""

from pathlib import Path

import os


# =====================================================
# BASE DIRECTORY
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# =====================================================
# SECURITY
# =====================================================

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-temp-key"
)

DEBUG = True

ALLOWED_HOSTS = ["*"]


# =====================================================
# APPLICATIONS
# =====================================================

INSTALLED_APPS = [

    'django.contrib.admin',

    'django.contrib.auth',

    'django.contrib.contenttypes',

    'django.contrib.sessions',

    'django.contrib.messages',

    'django.contrib.staticfiles',

    'game',

]


# =====================================================
# MIDDLEWARE
# =====================================================

MIDDLEWARE = [

    'django.middleware.security.SecurityMiddleware',

    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',

    'django.middleware.common.CommonMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',

    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]


# =====================================================
# URLS
# =====================================================

ROOT_URLCONF = 'animalsite.urls'


# =====================================================
# TEMPLATES
# =====================================================

TEMPLATES = [

    {

        'BACKEND':
        'django.template.backends.django.DjangoTemplates',

        'DIRS': [],

        'APP_DIRS': True,

        'OPTIONS': {

            'context_processors': [

                'django.template.context_processors.request',

                'django.contrib.auth.context_processors.auth',

                'django.contrib.messages.context_processors.messages',

            ],

        },

    },

]


# =====================================================
# WSGI
# =====================================================

WSGI_APPLICATION = 'animalsite.wsgi.application'


# =====================================================
# DATABASE
# =====================================================

import dj_database_url

DATABASES = {

    'default': dj_database_url.config(

        default=os.getenv("DATABASE_URL")

    )

}


# =====================================================
# PASSWORD VALIDATION
# =====================================================

AUTH_PASSWORD_VALIDATORS = [

    {

        'NAME':
        'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',

    },

    {

        'NAME':
        'django.contrib.auth.password_validation.MinimumLengthValidator',

    },

    {

        'NAME':
        'django.contrib.auth.password_validation.CommonPasswordValidator',

    },

    {

        'NAME':
        'django.contrib.auth.password_validation.NumericPasswordValidator',

    },

]


# =====================================================
# INTERNATIONALIZATION
# =====================================================

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# =====================================================
# STATIC FILES
# =====================================================

STATIC_URL = 'static/'

STATIC_ROOT = BASE_DIR / "staticfiles"


# =====================================================
# EMAIL CONFIGURATION (BREVO)
# =====================================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp-relay.brevo.com'

EMAIL_PORT = 587

EMAIL_HOST_USER = os.getenv(
    "EMAIL_HOST_USER"
)

EMAIL_HOST_PASSWORD = os.getenv(
    "EMAIL_HOST_PASSWORD"
)

EMAIL_USE_TLS = True


# =====================================================
# DEFAULT AUTO FIELD
# =====================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
