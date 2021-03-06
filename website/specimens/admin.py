from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django import forms

from mptt.admin import DraggableMPTTAdmin

from .models import (Specimen, SpecimenLocation, Person, Fixation, Station, Expedition, SpecimenPicture, Taxon,
                     Bioregion, Gear)
from .widgets import LatLongWidget


# Custom form to provide lat/lon widget instead of OL map.
class MyAdminForm(forms.ModelForm):

    class Meta:
        model = Station
        fields = "__all__"
        widgets = {
            "coordinates": LatLongWidget
        }


class SpecimenPictureInline(admin.TabularInline):
    model = SpecimenPicture


class HasFKListFilter(admin.SimpleListFilter):
    def lookups(self, request, model_admin):
        return (
            ('yes', _('Yes')),
            ('no', _('No')),
        )

    def queryset(self, request, queryset):
        lookup_key = '{0}__isnull'.format(self.fk_field_name)

        if self.value() == 'yes':
            return queryset.filter(**{lookup_key: False})
        if self.value() == 'no':
            return queryset.filter(**{lookup_key: True})


class HasTaxonListFilter(HasFKListFilter):
    parameter_name = 'has_taxon'
    fk_field_name = 'taxon'
    title = _('Attached to a Taxon')


class HasPicturesListFilter(HasFKListFilter):
    parameter_name = 'has_pictures'
    fk_field_name = 'specimenpicture'
    title = _('Has pictures')


class HasGearListFilter(HasFKListFilter):
    parameter_name = 'has_gear'
    fk_field_name = 'gear'
    title = _('Has gear')


@admin.register(Specimen)
class SpecimenAdmin(admin.ModelAdmin):
    list_display = ('specimen_id', 'station', 'has_picture', 'initial_scientific_name', 'taxon',
                    'uncertain_identification', 'identified_by', 'specimen_location', 'vial', 'bioregion', 'fixation')
    list_filter = ('identified_by', 'specimen_location', 'fixation', 'station__expedition', 'bioregion',
                   'uncertain_identification', HasTaxonListFilter, HasPicturesListFilter)
    search_fields = ['initial_scientific_name', 'specimen_id']
    # TODO: document searchable fields in template? (https://stackoverflow.com/questions/11411622/add-help-text-for-search-field-in-admin-py)

    fieldsets = (
        (None, {
            'fields': ('specimen_id',
                      ('taxon', 'uncertain_identification', 'initial_scientific_name'),
                      'station',
                      'identified_by',
                      'specimen_location',
                      'bioregion',
                      'fixation',
                      ('vial', 'vial_size'),
                      'mnhn_number',
                      'mna_code',
                      'bold_process_id',
                      'bold_sample_id',
                      'bold_bin',
                      'sequence_name',
                      'sequence_fasta',
                       'additional_data',
                      'comment')
                }),
        ('Isotopes', {
            'classes': ('collapse',),
            'fields': (('isotope_d13C', 'isotope_d15N', 'isotope_d34S'),
                       ('isotope_percentN', 'isotope_percentC', 'isotope_percentS'),
                       'isotope_C_N_proportion')
        }),
    )

    readonly_fields = ('initial_scientific_name', 'isotope_C_N_proportion')

    inlines = [
        SpecimenPictureInline,
    ]

    def has_picture(self, obj):
        return obj.has_pictures()
    has_picture.short_description = 'Has pictures?'
    has_picture.boolean = True


@admin.register(Gear)
class GearAdmin(admin.ModelAdmin):
    pass


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
    form = MyAdminForm

    list_display = ('name', 'expedition', 'coordinates_str', 'depth_str')
    list_filter = ('expedition', HasGearListFilter)

    fields = ('name',
              'expedition',
              ('capture_date_start', 'capture_date_end', 'initial_capture_year', 'initial_capture_date'),
              'coordinates',
              'depth',
              'gear'
    )

    readonly_fields = ('initial_capture_year', 'initial_capture_date')

    class Media:
        css = {
             "all": ("https://cdnjs.cloudflare.com/ajax/libs/ol3/3.15.1/ol.css",)
        }

        js = ("https://cdnjs.cloudflare.com/ajax/libs/proj4js/2.3.3/proj4.js",
              "https://cdnjs.cloudflare.com/ajax/libs/ol3/3.15.1/ol.js")


@admin.register(Expedition)
class ExpeditionAdmin(admin.ModelAdmin):
    pass


@admin.register(SpecimenPicture)
class SpecimenPictureAdmin(admin.ModelAdmin):
    fields = ('specimen', 'image', 'high_interest')


@admin.register(Taxon)
class TaxonAdmin(DraggableMPTTAdmin):
    pass


@admin.register(Bioregion)
class BioreginAdmin(admin.ModelAdmin):
    pass

admin.site.site_header = 'Astapor administration'