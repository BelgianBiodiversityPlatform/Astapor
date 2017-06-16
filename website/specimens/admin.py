from django.contrib import admin

from django import forms
from .models import Specimen, SpecimenLocation, Person, Fixation
from .widgets import LatLongWidget


# Custom form to provide lat/lon widget instead of OL map.
class MyAdminForm(forms.ModelForm):

    class Meta:
        model = Specimen
        fields = "__all__"
        widgets = {
            'coords': LatLongWidget
        }


class SpecimenAdmin(admin.ModelAdmin):
    form = MyAdminForm

    list_display = ('specimen_id', 'scientific_name', 'identified_by', 'specimen_location', 'depth_str', 'fixation')
    list_filter = ('identified_by', 'specimen_location', 'fixation')
    search_fields = ['scientific_name']

class SpecimenLocationAdmin(admin.ModelAdmin):
    pass

class PersonAdmin(admin.ModelAdmin):
    pass

class FixationAdmin(admin.ModelAdmin):
    pass

admin.site.register(Specimen, SpecimenAdmin)
admin.site.register(SpecimenLocation, SpecimenLocationAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Fixation, FixationAdmin)