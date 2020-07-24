import os
import datetime

from .secret_data import SECRET_KEY, TIME_ZONE, DEBUG
from .secret_data import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, ALLOWED_HOST, DB_PORT
from .secret_data import FRONTEND_URL

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', SECRET_KEY)

DEBUG = bool(os.environ.get('DJANGO_DEBUG', DEBUG))

if not DEBUG:

    CSRF_COOKIE_SECURE = True

    SECURE_SSL_REDIRECT = True

    SESSION_COOKIE_SECURE = True

    SECURE_CONTENT_TYPE_NOSNIFF = True

    SECURE_BROWSER_XSS_FILTER = True

    SESSION_EXPIRE_AT_BROWSER_CLOSE = True

ALLOWED_HOSTS = [
                os.environ.get('ALLOWED_HOST', ALLOWED_HOST)
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'territories.apps.TerritoriesConfig',
    'appointment_requests.apps.AppointmentRequestsConfig',
    'doctors.apps.DoctorsConfig',
    'insurance_companies.apps.InsuranceCompaniesConfig',
    'invoices.apps.InvoicesConfig',
    'rest_framework',
    'rest_framework_jwt',
    'corsheaders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

#apps settings

if DEBUG:
    CORS_ORIGIN_ALLOW_ALL = True
else:
    CORS_ORIGIN_WHITELIST = [
                        FRONTEND_URL,
    ]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAdminUser',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
}

JWT_AUTH = {
    'JWT_ALLOW_REFRESH': True,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(seconds=600),
}


ROOT_URLCONF = 'medical_center.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'medical_center.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE'  : 'django.db.backends.mysql',
        'NAME'    : os.environ.get('DB_NAME', DB_NAME),
        'USER'    : os.environ.get('DB_USER', DB_USER),
        'PASSWORD': os.environ.get('DB_PASSWORD', DB_PASSWORD),
        'HOST'    : os.environ.get('DB_HOST', DB_HOST),
        'PORT'    : os.environ.get('DB_PORT', DB_PORT),
        'OPTIONS' : {
            'autocommit': True,
            'charset': 'utf8',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DATE_FORMAT = 'j E Y'

TIME_ZONE = os.environ.get('TIME_ZONE', TIME_ZONE)

TIME_FORMAT = 'H:i'

DATETIME_FORMAT = 'j E Y H:i'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
