"""
Django settings for api project.

Generated by 'django-admin startproject' using Django 4.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
from pathlib import Path
import dj_database_url
#import redis
from urllib.parse import urlparse

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
AUTH_PROFILE_MODULE = 'core.Profile'
CSRF_COOKIE_SECURE = True

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

if os.getenv('ENV') == 'production':
    ALLOWED_HOSTS = ['nlpeace-0c427559664a.herokuapp.com','https://nlpeace-0c427559664a.herokuapp.com', 'https://nlpeace.com', 'https://nlpeace.herokuapp.com']

    CSRF_TRUSTED_ORIGINS = [
    'https://nlpeace-0c427559664a.herokuapp.com',
    'https://nlpeace.com', 'https://nlpeace.herokuapp.com'
    ]
else:
    ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'core.tests',
    'api',
    'chat'
]

MIDDLEWARE = [
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'api.urls'
AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'api.wsgi.application'
ASGI_APPLICATION = "api.asgi.application"
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
if 'DATABASE_URL' in os.environ:
    DEBUG = True
    #Heroku prod db
    DATABASES = {'default': dj_database_url.config(default=os.environ.get('DATABASE_URL'))}
else:
    DEBUG = True
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'HOST': 'db',
            'NAME': 'devdb',
            'USER': 'devuser',
            'PASSWORD': 'changeme',
            'PORT': '5432'
            # 'HOST': os.environ.get('DB_HOST'),
            # 'NAME': os.environ.get('DB_NAME'),
            # 'USER': os.environ.get('DB_USER'),
            # 'PASSWORD': os.environ.get('DB_PASS'),
        }
    }

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
WHITENOISE_MAX_AGE = 31536000  # 1 year in seconds
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
WHITENOISE_MANIFEST_STRICT = False

STATICFILES_DIR=[
    os.path.join(BASE_DIR,'static')
    #os.path.join(BASE_DIR, 'chat/static')
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
WHITENOISE_MAX_AGE = 31536000  # 1 year in seconds
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
WHITENOISE_MANIFEST_STRICT = False


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#We define where profile pictures and banner pictures will be stored
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'api','core', 'media')

#SMTP Configuration
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND')
EMAIL_HOST= os.getenv('EMAIL_HOST')
EMAIL_PORT= os.getenv('EMAIL_PORT')
EMAIL_USE_TLS= os.getenv('EMAIL_USE_TLS')
EMAIL_HOST_USER= os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD= os.getenv('EMAIL_HOST_PASSWORD')

#redis stuff
# Redis configuration
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')
REDIS_TLS_URL = os.environ.get('REDIS_TLS_URL', 'redis://localhost:6379')
#redis_instance = redis.StrictRedis.from_url(REDIS_URL)
# Channels
if os.getenv('ENV') == 'production':
    redis_url = urlparse(os.environ.get('REDIS_URL', ''))
    redis_host = redis_url.hostname
    redis_port = redis_url.port
    redis_password = redis_url.password

    ASGI_APPLICATION = "api.asgi.application"
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [(redis_host, redis_port)],
                "password": redis_password,
            },
        },
    }
    if redis_password:
        CHANNEL_LAYERS["default"]["CONFIG"]["password"] = redis_password
else:
    REDIS_HOST = os.getenv('REDIS_HOST')
    REDIS_PORT = os.getenv('REDIS_PORT')
    ASGI_APPLICATION = "api.asgi.application"
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [(REDIS_HOST, int(REDIS_PORT))],#"hosts": [("127.0.0.1", 6379)],
            },
        },
    }

GIPHY_API_KEY = os.getenv('GIPHY_API_KEY')

# The number of days allowed to elapse without a user mentioning a
# topic before it is assumed they are no longer interested in it.
INTEREST_DAYS_THRESHOLD = 10

# The degree to which a user must have expressed interest in a topic for a advertisement
# covering it to be included in the list of ads shown to them.
TOPIC_INCLUSION_THRESHOLD = 0.7

AD_MIX_RATE = 5

AD_SELECTION_STRATEGY = 'constant'
