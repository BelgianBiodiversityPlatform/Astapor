from django.contrib import admin
from specimens.models import Specimen

class SpecimenAdmin(admin.ModelAdmin):
    pass

admin.site.register(Specimen, SpecimenAdmin)
