"""
WSGI config for monitor_web project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
import sys
path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(path)
# sys.path.append("/var/www/monitor_web/")
os.environ["DJANGO_SETTINGS_MODULE"] = "monitor_web.settings"

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
