"""
WSGI config for data_channel project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
import sys
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "data_channel.settings")
# sys.path.append("/var/www/data_channel/")
path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(path)
os.environ["DJANGO_SETTINGS_MODULE"] = "data_channel.settings"

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
