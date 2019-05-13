from django.contrib import admin
from django.apps import apps

# Register your models here.

test = {}

for x in apps.all_models['parking']:
    admin.site.register(apps.all_models['parking'][x], test.get(
        apps.all_models['parking'][x].__name__))