"""
Django settings for opencodelists project.

Generated by 'django-admin startproject' using Django 3.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""
import os
import sys

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import ignore_logger

from services.logging import logging_config_dict

# Patch sqlite3 to ensure recent version
__import__("pysqlite3")
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


IN_PRODUCTION = bool(os.environ.get("IN_PRODUCTION"))


if IN_PRODUCTION:
    SECRET_KEY = os.environ["SECRET_KEY"]
    DEBUG = False
    ALLOWED_HOSTS = [os.environ["ALLOWED_HOST"]]

    # This setting causes infinite redirects
    # SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

else:
    SECRET_KEY = "secret"
    DEBUG = not os.environ.get("NO_DEBUG")
    ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "opencodelists",
    "builder",
    "codelists",
    "coding_systems.bnf",
    "coding_systems.ctv3",
    "coding_systems.readv2",
    "coding_systems.snomedct",
    "mappings.rctctv3map",
    "mappings.ctv3sctmap2",
    "corsheaders",
    "crispy_forms",
    "django_extensions",
    "debug_toolbar",
    "markdown_filter",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django_structlog.middlewares.RequestMiddleware",
]

ROOT_URLCONF = "opencodelists.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "opencodelists.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}


# Custom user model

AUTH_USER_MODEL = "opencodelists.User"

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Post-login
LOGIN_REDIRECT_URL = "codelists:index"


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static", "dist")]
STATIC_URL = "/static/"
WHITENOISE_USE_FINDERS = True


# Logging
LOGGING = logging_config_dict


# Tests
TEST_RUNNER = "opencodelists.django_test_runner.PytestTestRunner"


# Crispy
CRISPY_TEMPLATE_PACK = "bootstrap4"


# Sentry
# ignore the request logging middleware, it creates ungrouped events by default
# https://docs.sentry.io/platforms/python/guides/logging/#ignoring-a-logger
ignore_logger("django_structlog.middlewares.request")

SENTRY_DSN = os.environ.get("SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        send_default_pii=True,
    )

# CORS

CORS_ORIGIN_ALLOW_ALL = True


MARKDOWN_FILTER_WHITELIST_TAGS = [
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "a",
    "p",
    "ul",
    "li",
    "code",
]


# Login/logout config
LOGOUT_REDIRECT_URL = "/"


# Debug Toolbar
INTERNAL_IPS = [
    "127.0.0.1",
]
