import os
import sys

sys.path.append(os.path.dirname(__file__))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DjangoProject1.settings")

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()
