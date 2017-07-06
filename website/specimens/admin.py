from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
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


@admin.register(Specimen)
class SpecimenAdmin(admin.ModelAdmin):
    form = MyAdminForm

    list_display = ('specimen_id', 'station', 'has_picture', 'taxon', 'initial_scientific_name', 'identified_by',
                    'specimen_location', 'depth_str', 'fixation')
    list_filter = ('identified_by', 'specimen_location', 'fixation', 'station__expedition', HasTaxonListFilter,
                   HasPicturesListFilter)
    search_fields = ['initial_scientific_name', 'specimen_id']
    # TODO: document searchable fields in template? (https://stackoverflow.com/questions/11411622/add-help-text-for-search-field-in-admin-py)

    fields = ('specimen_id', ('taxon', 'initial_scientific_name'), 'station', 'coords', 'depth', 'identified_by',
              'specimen_location', 'fixation', 'comment')
    readonly_fields = ('initial_scientific_name',)

    inlines = [
        SpecimenPictureInline,
    ]

    def has_picture(self, obj):
        return obj.has_pictures()
    has_picture.short_description = 'Has pictures?'
    has_picture.boolean = True

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