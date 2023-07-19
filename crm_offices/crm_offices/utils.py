from django.contrib import admin
from datetime import datetime

class CustomStr:
    def __str__(self):
        if hasattr(self, 'title'):
            return self.title
        elif hasattr(self, 'name'):
            return self.name
        else:
            return str(self.id)


def safe_get(Model, **kwargs):
    try:
        return Model.objects.get(**kwargs)
    except Model.MultipleObjectsReturned:
        return Model.objects.filter(**kwargs).last()
    except Model.DoesNotExist:
        return None


def get_year(session):
    return session.get('year', datetime.today().year)


def get_office(session):
    return session.get('office', None)


class PrePopulatedSlug(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}