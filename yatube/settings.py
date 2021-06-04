import os
from pathlib import PurePath

from dotenv import load_dotenv


load_dotenv()

BASE_DIR = PurePath(__file__).parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

DEBUG = os.getenv('DJANGO_DEBUG', 'false').lower() in {'yes', '1', 'true'}

ALLOWED_HOSTS = (
    os.getenv('DOMAIN_NAME'),
    'localhost',
    '127.0.0.1',
)


# Application definition
INSTALLED_APPS = (
    'users',
    'posts',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'sorl.thumbnail',
)

MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

if DEBUG:
    INSTALLED_APPS += (
        'debug_toolbar',
    )
    MIDDLEWARE = (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ) + MIDDLEWARE


ROOT_URLCONF = 'yatube.urls'

TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
TEMPLATES = [  # noqa: WPS407
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'yatube.wsgi.application'


# Database
DATABASES = {  # noqa: WPS407
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
}


# Password validation
_PASS = 'django.contrib.auth.password_validation'  # noqa: S105
AUTH_PASSWORD_VALIDATORS = (
    {'NAME': '{0}.UserAttributeSimilarityValidator'.format(_PASS)},
    {'NAME': '{0}.MinimumLengthValidator'.format(_PASS)},
    {'NAME': '{0}.CommonPasswordValidator'.format(_PASS)},
    {'NAME': '{0}.NumericPasswordValidator'.format(_PASS)},
)


# Internationalization
LANGUAGE_CODE = 'ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

INTERNAL_IPS = (
    '127.0.0.1',
)


# Login
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = 'index'
LOGOUT_REDIRECT_URL = 'index'

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = os.path.join(BASE_DIR, 'sent_emails')

SITE_ID = 1

CACHES = {  # noqa: WPS407
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
}
