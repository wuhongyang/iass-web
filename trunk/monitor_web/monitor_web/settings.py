"""
Django settings for monitor_web project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'dln4ay(0$1)7#v7f9$fdl^sf3f@a7s4-y&!!2p9$m6sq5c(441'

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'cm_alarm',
    'cm_data',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'monitor_web.urls'

WSGI_APPLICATION = 'monitor_web.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'NAME': 'mapdb',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'root',
        'PASSWORD': 'cci',
        'HOST': '10.10.82.111',
        'PORT': '3306',
    },
    'cmuserdb': {
        'NAME': 'db1',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'root',
        'PASSWORD': 'cci',
        'HOST': '10.10.82.111',
        'PORT': '3306',
    },
    'novadb': {
        'NAME': 'nova',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'root',
        'PASSWORD': 'cci',
        'HOST': '10.10.82.111',
        'PORT': '3306',
    }
}

DATABASE_ROUTERS = ['monitor_web.dbrouter.DBRouter']
DATACHANNEL_PORT = '82'
PAGE_COUNT = '20'
PHYSICAL_RRD_BASE_PATH = '/var/lib/ganglia/rrds/HOST-INFO/'
GMOND_HOST = '10.10.82.111'
GMOND_PORT = '8657'
VMWARE_DATACHANNEL_IP = '10.10.82.111'

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

# logging.basicConfig(
# 	level = logging.INFO,
# 	format = '%(asctime)s %(levelname)s %(module)s.%(funcName)s Line:%(lineno)d%(message)s',
# 	filename = os.path.join(BASE_DIR, 'logs/monitor_web.log'),
# )

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

# TEMPLATE_DIRS = (
#     os.path.join(BASE_DIR,  'templates'),
# )