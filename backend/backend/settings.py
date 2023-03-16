"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 3.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
from decouple import config


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-av!*96e0e^r3i6#57oe7v2sm4ur5we^-kxhh8=p-#g3c)g5gjj"
# SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
PRODUCTION = False
# DEBUG = config('DEBUG', default=True, cast=bool)


ALLOWED_HOSTS = ["0.0.0.0", "localhost", "127.0.0.1", "oncodash.ing.unimore.it", "http://0.0.0.0:3000/", "http://0.0.0.0:3001"]


# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # own apps
    "core",
    "explainer",
    "clin_overview",
    "side_effects",
    # third-party
    "rest_framework",
    "corsheaders",
    'rest_framework.authtoken',
]

CORS_ALLOWED_ORIGINS = [
    "http://0.0.0.0:3000", #For React Project
    "http://oncodash.ing.unimore.it:3000",
    "http://0.0.0.0:8888",  #For Django Project
    "http://oncodash.ing.unimore.it:8888",
    "https://0.0.0.0:3000", #For React Project
    "https://oncodash.ing.unimore.it:3000",
    "https://0.0.0.0:8888",  #For Django Project
    "https://oncodash.ing.unimore.it:8888",
]

CORS_ORIGIN_ALLOW_ALL = True

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "backend.urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR.parent / "oncodash-app"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.contrib.auth.login", #
                "django.contrib.auth.logout",#
            ],
        },
    },
]

WSGI_APPLICATION = "backend.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = Path(BASE_DIR / "static")
STATICFILES_DIRS = [BASE_DIR.parent / "oncodash-app/"]


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "core.User"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
}



def skip_lib_python(record):
    """Filter that removes "File seen" events on a *lib/python* file."""
    msg = record.msg
    if msg and msg.startswith("File") and len(record.args)>0:
        path = str(record.args[0].resolve())
        if "lib/python" in path:
            return False
    return True

def skip_node_modules(record):
    """Filter that removes "File seen" events on a *node_modules* file."""
    msg = record.msg
    if msg and msg.startswith("File") and len(record.args)>0:
        path = str(record.args[0].resolve())
        if "node_modules" in path:
            return False
    return True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        # use Django's built in CallbackFilter to point to our filter 
        'skip_lib_python': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': skip_lib_python
        },
        'skip_node_modules': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': skip_node_modules
        }
    },
    'formatters': {
        # django's default formatter
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[%(server_time)s] %(message)s',
        }
    },
    'handlers': {
        'my_log_handler': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'filters': ['skip_lib_python','skip_node_modules'],
            'class': 'logging.FileHandler',
            'filename': Path(BASE_DIR, 'django.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['my_log_handler'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': True,
        },
    },
}
