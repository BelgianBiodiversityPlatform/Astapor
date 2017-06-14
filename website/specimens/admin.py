from django.contrib import admin

from django import forms
from .models import Specimen
from .widgets import LatLongWidget


# Custom form to provide lat/lon widget instead of OL map.
class MyAdminForm(forms.ModelForm):

    class Meta:
        model = Specimen
        fields = "__all__"
        widgets = {
            'location': LatLongWidget
        }


class SpecimenAdmin(admin.ModelAdmin):
    form = MyAdminForm

admin.site.register(Specimen, SpecimenAdmin)
