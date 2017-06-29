from django.contrib import admin

from django import forms

from mptt.admin import DraggableMPTTAdmin

from .models import Specimen, SpecimenLocation, Person, Fixation, Station, Expedition, SpecimenPicture, Taxon
from .widgets import LatLongWidget


# Custom form to provide lat/lon widget instead of OL map.
class MyAdminForm(forms.ModelForm):

    class Meta:
        model = Specimen
        fields = "__all__"
        widgets = {
            'coords': LatLongWidget
        }


class SpecimenPictureInline(admin.TabularInline):
    model = SpecimenPicture

@admin.register(Specimen)
class SpecimenAdmin(admin.ModelAdmin):
    form = MyAdminForm

    list_display = ('specimen_id', 'station', 'initial_scientific_name', 'identified_by', 'specimen_location', 'depth_str', 'fixation')
    list_filter = ('identified_by', 'specimen_location', 'fixation', 'station__expedition')
    search_fields = ['initial_scientific_name', 'specimen_id']
    # TODO: document searchable fields in template? (https://stackoverflow.com/questions/11411622/add-help-text-for-search-field-in-admin-py)

    inlines = [
        SpecimenPictureInline,
    ]

    class Media:
        css = {
             "all": ("https://cdnjs.cloudflare.com/ajax/libs/ol3/3.15.1/ol.css",)
        }

        js = ("https://cdnjs.cloudflare.com/ajax/libs/proj4js/2.3.3/proj4.js",
              "https://cdnjs.cloudflare.com/ajax/libs/ol3/3.15.1/ol.js")

@admin.register(SpecimenLocation)
class SpecimenLocationAdmin(admin.ModelAdmin):
    pass


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    pass

@admin.register(Fixation)
class FixationAdmin(admin.ModelAdmin):
    pass

@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ('name', 'expedition')
    list_filter = ('expedition', )

@admin.register(Expedition)
class ExpeditionAdmin(admin.ModelAdmin):
    pass

@admin.register(SpecimenPicture)
class SpecimenPictureAdmin(admin.ModelAdmin):
    fields = ('specimen', 'image', 'high_interest')

@admin.register(Taxon)
class TaxonAdmin(DraggableMPTTAdmin):
    pass

admin.site.site_header = 'Astapor administration'