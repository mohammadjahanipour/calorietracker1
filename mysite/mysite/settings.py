"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 3.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import django_heroku
from pathlib import Path
import os
import logging.config
import cloudinary


# # Base Configuration ========================================================
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", False) == "True"


# Specify the context processors as follows:
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Already defined Django-related contexts here

                # `allauth` needs this from django
                'django.template.context_processors.request',
            ],
        },
    },
]

ALLOWED_HOSTS = []

# # Email Configuration ========================================================
ADMINS = [("CT", "calorietrackerio@gmail.com")]
MANAGERS = ADMINS

DEFAULT_FROM_EMAIL = "calorietrackerio@gmail.com"
SERVER_EMAIL = "calorietrackerio@gmail.com"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = "calorietrackerio@gmail.com"
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_PORT = 587
EMAIL_USE_TLS = True


# # Stripe Configuration ========================================================
STRIPE_LIVE_PUBLIC_KEY = os.getenv("STRIPE_LIVE_PUBLIC_KEY")
STRIPE_LIVE_SECRET_KEY = os.getenv("STRIPE_LIVE_SECRET_KEY")
STRIPE_TEST_PUBLIC_KEY = os.getenv("STRIPE_TEST_PUBLIC_KEY")
STRIPE_TEST_SECRET_KEY = os.getenv("STRIPE_TEST_SECRET_KEY")
STRIPE_LIVE_MODE = os.getenv("STRIPE_LIVE_MODE", False)
DJSTRIPE_WEBHOOK_VALIDATION = None

# # Cloudinary Configuration ========================================================
cloudinary.config(
    cloud_name="calorietracker-io",
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)

# # Log in/out Configuration ========================================================
LOGIN_REDIRECT_URL = "/logdata"
LOGOUT_REDIRECT_URL = "/"
LOGIN_URL = "login"


# # Logging Configuration ========================================================
# Get loglevel from env
# LOGGING_CONFIG = None
LOGLEVEL = os.getenv("DJANGO_LOGLEVEL", "info").upper()

logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "console": {
                "format": "%(asctime)s %(levelname)s [%(name)s:%(lineno)s] %(module)s %(process)d %(thread)d %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "console",
            },
            "mail_admins": {
                "level": "ERROR",
                "class": "django.utils.log.AdminEmailHandler",
                "email_backend": EMAIL_BACKEND,
                "reporter_class": "django.views.debug.ExceptionReporter",
            },
        },
        "loggers": {
            "": {
                "level": LOGLEVEL,
                "handlers": [
                    "console",
                    "mail_admins",
                ],
            },
        },
    }
)


# # Applications Configuration ========================================================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",  # needed by pinax.referrals
    "calorietracker",
    # third party packages/apps
    "safedelete",
    "crispy_forms",
    "bootstrap_datepicker_plus",
    "actstream",
    "chartjs",
    "measurement",
    "pinax.referrals",
    "djstripe",
    "cloudinary",
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.discord',
]

# 1 == dev domaine and sitename
# 2 == production domaine and sitename
SITE_ID = 1 if DEBUG else 2  # see migration 0008_Configure_Site_Names for more info

CRISPY_TEMPLATE_PACK = "bootstrap4"
PINAX_REFERRALS_SECURE_URLS = False if DEBUG else True


# # Middleware ========================================================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "pinax.referrals.middleware.SessionJumpingMiddleware",
]

# # URLCONF ========================================================
ROOT_URLCONF = "mysite.urls"
WSGI_APPLICATION = "mysite.wsgi.application"

# # Templates ========================================================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # `allauth` needs this from django
                'django.template.context_processors.request',
            ],
        },
    },
]


# # Database(s) ========================================================
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# # Password Validation ========================================================
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators
# AUTH_PASSWORD_VALIDATORS = [
#     {
#         "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
#     },
#     {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", },
#     {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator", },
#     {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator", },
# ]


# # Internationalization ========================================================
# https://docs.djangoproject.com/en/3.1/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# # Static Files(CSS, JavaScript, Images) ========================================================
# https://docs.djangoproject.com/en/3.1/howto/static-files/
STATIC_URL = "/static/"

# # Heroku ========================================================
# Configure Django App for Heroku.
django_heroku.settings(locals())

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
]

# # Provider specific settings
# https://django-allauth.readthedocs.io/en/latest/providers.html#facebook
SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
        'METHOD': 'js_sdk',
        'SDK_URL': '//connect.facebook.net/{locale}/sdk.js',
        'SCOPE': ['email', 'public_profile'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'INIT_PARAMS': {'cookie': True},
        'FIELDS': [
            'id',
            'first_name',
            'last_name',
            'middle_name',
            'name',
            'name_format',
            'picture',
            'short_name'
        ],
        'EXCHANGE_TOKEN': True,
        # 'LOCALE_FUNC': 'path.to.callable',
        'VERIFIED_EMAIL': False,
        'VERSION': 'v7.0',
    },
    'discord': {
        'APP': {
            'client_id': os.getenv("DISCORD_CLIENT_ID"),
            'secret': os.getenv("DISCORD_SECRET"),
            'key': os.getenv("DISCORD_KEY")
        }
    }
}
