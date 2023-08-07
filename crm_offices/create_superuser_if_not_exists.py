import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crm_offices.settings")
django.setup()

from django.contrib.auth.models import User

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')