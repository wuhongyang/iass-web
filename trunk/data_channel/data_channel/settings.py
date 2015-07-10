"""
Django settings for data_channel project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
# import logging
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '2p%4s^+6en-37mr$-5w_6pqlkjgi098$l(qtvx@&4fmr*ym(j-'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
#    'django.contrib.admin',
#    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rrdapi',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
#    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
#    'django.middleware.crossdomainxhr.XsSharing',
)

# logging.basicConfig(
# 	level = logging.INFO,
# 	format = '%(asctime)s %(levelname)s %(module)s.%(funcName)s Line:%(lineno)d%(message)s',
# 	filename = os.path.join(BASE_DIR, 'logs/data_channel.log'),
# )


ROOT_URLCONF = 'data_channel.urls'

WSGI_APPLICATION = 'data_channel.wsgi.application'
RRD_BASE_PATH = '/var/lib/ganglia/rrds/'

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
    }
}


TEMPLATE_DIRS = (       
    os.path.join(BASE_DIR, 'templates'),

)
APPEND_SLASH = False
# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

#TIME_ZONE = 'UTC'
TIME_ZONE = 'Asia/Shanghai' #UTC+8

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
