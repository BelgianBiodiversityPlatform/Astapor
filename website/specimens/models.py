from django.contrib.gis.db import models
from django.contrib.postgres.fields import FloatRangeField, HStoreField
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator

from django.conf import settings

from mptt.models import MPTTModel, TreeForeignKey

from .validators import plausible_specimen_date, StrictlyMinValueValidator

UNKNOWN_STATION_NAME = '<Unknown>'  # Sometimes we need a "fake" station to link Specimen to Expedition

# Ranks: Sometimes names are used as an identifier...
SPECIES_RANK_NAME = "Species"
SUBGENUS_RANK_NAME = "Subgenus"
GENUS_RANK_NAME = "Genus"
FAMILY_RANK_NAME = "Family"


class TaxonRank(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class TaxonStatus(models.Model):
    name = models.CharField(max_length=100)


class SpeciesManager(models.Manager):
    def get_queryset(self):
        return super(SpeciesManager, self).get_queryset().filter(rank__name=SPECIES_RANK_NAME)


class GenusManager(models.Manager):
    def get_queryset(self):
        return super(GenusManager, self).get_queryset().filter(rank__name=GENUS_RANK_NAME)


class FamilyManager(models.Manager):
    def get_queryset(self):
        return super(FamilyManager, self).get_queryset().filter(rank__name=FAMILY_RANK_NAME)


class TaxonManager(models.Manager):
    def get_subgenus_from_parentheses_form(self, parentheses_string):
        # Given a string such as "Cheiraster (Luidiaster)", returns the matching subgenus, if exists
        genus_name, subgenus_name = parentheses_string.replace('(', '').replace(')', '').split()
        try:
            return self.get_queryset().get(rank__name=SUBGENUS_RANK_NAME,
                                           parent__name=genus_name,
                                           name=subgenus_name)
        except ObjectDoesNotExist:
            return None


class Taxon(MPTTModel):
    name = models.CharField(max_length=100)
    rank = models.ForeignKey(TaxonRank, on_delete=models.CASCADE)
    status = models.ForeignKey(TaxonStatus, on_delete=models.CASCADE, null=True, blank=True)
    aphia_id = models.IntegerField(null=True, blank=True)
    authority = models.CharField(max_length=100, blank=True)

    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True,
                            on_delete=models.CASCADE)

    objects = TaxonManager()

    species_objects = SpeciesManager()
    genus_objects = GenusManager()
    family_objects = FamilyManager()

    def is_species(self):
        return self.rank.name == SPECIES_RANK_NAME

    def is_subgenus(self):
        return self.rank.name == SUBGENUS_RANK_NAME

    def is_genus(self):
        return self.rank.name == GENUS_RANK_NAME

    def species_name(self):  # Only work for species!!
        if self.parent.is_subgenus():
            name = "{genus_name} ({subgenus_name}) {species_name}".format(species_name=self.name,
                                                                          subgenus_name=self.parent.name,
                                                                          genus_name=self.parent.parent.name)
        else:
            name = "{genus_name} {species_name}".format(species_name=self.name, genus_name=self.parent.name)
        return name

    def __str__(self):
        # Specific representation for Species
        if self.is_species():
            name = self.species_name()
        else:
            name = self.name

        return "{name} [{rank}]".format(name=name, rank=self.rank)

    class MPTTMeta:
        order_insertion_by = ['name']


class Bioregion(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Person(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    class Meta:
        unique_together = ("first_name", "last_name")
        verbose_name_plural = "people"

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class SpecimenLocation(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Fixation(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Expedition(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Gear(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class StationManager(models.Manager):
    def possible_inconsistent_duplicate(self, name, expedition, coordinates, depth, gear, capture_date_start,
                                        capture_date_end):
        """If a similar (but not identical) station already exists, return it.

        Returns false in other cases (for example if perfectly equal, or if nothing similar exists)
        """

        if self.filter(name=name, expedition=expedition).count() == 1:
            try:
                self.get(name=name, expedition=expedition, coordinates=coordinates, depth=depth, gear=gear,
                         capture_date_start=capture_date_start, capture_date_end=capture_date_end)
                return False   # It's identical
            except ObjectDoesNotExist:
                return self.get(name=name, expedition=expedition)
        else:
            return False  # nothing similar exists


class Station(models.Model):
    name = models.CharField(max_length=100)
    expedition = models.ForeignKey(Expedition, on_delete=models.CASCADE)

    # Date management:
    # In initial data, we have messy and sometimes imprecise dates in two fields (date and year)
    # - Those two are imported in the raw initial_date and initial_year fields (read-only so they can't be changed after
    # import)
    # For 'real app use', we use the capture_date_start and capture_date_end date fields (avoided Postgres native
    # daterange type, since it always returns [,) intervals.
    #
    # At import, we try to figure out the messy things in raw_* fields to populate capture_date_start and
    # capture_date_end.
    #
    # For DarwinCore export, we'll probably show a single date when capture_date_start == capture_date_end.
    initial_capture_year = models.CharField(max_length=5, blank=True)
    initial_capture_date = models.CharField(max_length=100, blank=True)
    capture_date_start = models.DateField(null=True, blank=True, validators=[plausible_specimen_date])
    capture_date_end = models.DateField(null=True, blank=True, validators=[plausible_specimen_date])

    coordinates = models.PointField(blank=True, null=True)
    depth = FloatRangeField(blank=True, null=True, help_text="Unit: meters.")

    gear = models.ForeignKey(Gear, blank=True, null=True, on_delete=models.CASCADE)

    objects = StationManager()

    def __str__(self):
        return "{station_name} ({expedition_name})".format(station_name=self.name, expedition_name=self.expedition.name)

    def clean(self):
        if ((self.capture_date_start and not self.capture_date_end) or
                (not self.capture_date_start and self.capture_date_end)):

            raise ValidationError("Both capture dates (or none) should be set!")

        if ((self.capture_date_start and self.capture_date_end) and
                (self.capture_date_end < self.capture_date_start)):
            raise ValidationError("Start date should be earlier than end date!")


    def long_str(self):
        return "{name} (from exp. {exp_name}) Point={coordinates} Depth={depth} Gear={gear} Initial year={i_year} Initial date={i_date} start_date={s_date} end_date={e_date}".format(
            name=self.name,
            exp_name=self.expedition,
            coordinates=self.coordinates_str(),
            depth=self.depth_str(),
            gear=self.gear,
            i_year=self.initial_capture_year,
            i_date=self.initial_capture_date,
            s_date=self.capture_date_start,
            e_date=self.capture_date_end
            )

    def depth_str(self):
        if self.depth:
            if self.depth.lower == self.depth.upper: # Single value
                str = "{depth}m.".format(depth=self.depth.lower)
            else:  # Real range
                str = '{min_depth}-{max_depth}m.'.format(min_depth=self.depth.lower, max_depth=self.depth.upper)
        else:  # No data
            str = '-'

        return str

    depth_str.short_description = 'Depth'

    def coordinates_str(self):
        if self.coordinates:
            return "{lat}, {lon}".format(lat=self.coordinates.y, lon=self.coordinates.x)

        return '-'

    coordinates_str.short_description = 'Coordinates'


class Specimen(models.Model):
    specimen_id = models.IntegerField(unique=True)  # ID from the lab, not Django's PK
    initial_scientific_name = models.CharField(max_length=100)
    taxon = models.ForeignKey(Taxon, null=True, blank=True, on_delete=models.CASCADE)
    uncertain_identification = models.BooleanField(default=False)
    identified_by = models.ForeignKey(Person, on_delete=models.CASCADE)
    specimen_location = models.ForeignKey(SpecimenLocation, on_delete=models.CASCADE)
    fixation = models.ForeignKey(Fixation, blank=True, null=True, on_delete=models.CASCADE)
    comment = models.TextField(blank=True, null=True)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)

    # Reference of the small container for the captured animal. Unique per expedition.
    vial = models.CharField(max_length=100, blank=True)

    vial_size = models.CharField(max_length=100, blank=True) # As text for now, we'll see later

    mnhn_number = models.CharField(max_length=100, blank=True)
    mna_code = models.CharField(max_length=100, blank=True)
    bold_process_id = models.CharField(max_length=100, blank=True)
    bold_sample_id = models.CharField(max_length=100, blank=True)
    bold_bin = models.CharField(max_length=100, blank=True)
    sequence_name = models.CharField(max_length=100, blank=True)
    sequence_fasta = models.TextField(blank=True)
    bioregion = models.ForeignKey(Bioregion, null=True, blank=True, on_delete=models.CASCADE)

    isotope_d13C = models.FloatField(' d13C', null=True, blank=True,   # Whitespace to avoid capitalization in forms
                                     validators=[MinValueValidator(-40), MaxValueValidator(-10)])
    isotope_d15N = models.FloatField(' d15N', null=True, blank=True,
                                     validators=[MinValueValidator(-5), MaxValueValidator(30)])
    isotope_d34S = models.FloatField(' d34S', null=True, blank=True)

    isotope_percentN = models.FloatField(' %N', null=True, blank=True,
                                         validators=[StrictlyMinValueValidator(0), MaxValueValidator(10)])  # 0 excluded
    isotope_percentC = models.FloatField(' %C', null=True, blank=True,
                                         validators=[StrictlyMinValueValidator(0), MaxValueValidator(30)])  # 0 excluded
    isotope_percentS = models.FloatField(' %S', null=True, blank=True,
                                         validators=[StrictlyMinValueValidator(0)])

    additional_data = HStoreField(blank=True, null=True)

    def isotope_C_N_proportion(self):
        if self.isotope_percentC and self.isotope_percentN:
            return self.isotope_percentC / self.isotope_percentN
        else:
            return '/'

    isotope_C_N_proportion.short_description = 'C/N proportions'

    def has_pictures(self):
        return self.specimenpicture_set.count() > 0

    def _check_field_unique_if_not_null(self, field_name, error_message):
        field_value = getattr(self, field_name)
        if field_value:
            is_new_record = self.pk is None

            matching_objects = Specimen.objects.filter(**{field_name: field_value})
            matching_objects_count = matching_objects.count()

            ok = False
            if matching_objects_count == 0:
                ok = True  # No match, no problem
            elif matching_objects_count == 1:
                if not is_new_record and matching_objects.get().pk == self.pk:
                    ok = True  # There's already one, but it seems it's me

            if not ok:
                raise ValidationError(error_message)

    def clean(self):
        is_new = self.pk is None

        if self.vial and not settings.DISABLE_VIAL_UNIQUENESS_VALIDATION:
            match_obj = Specimen.objects.filter(vial=self.vial, station__expedition=self.station.expedition)
            if is_new:  # New specimen: should have 0
                if match_obj.count() > 0:
                    raise ValidationError("Vial should be unique for a given expedition")
            else:
                # Existing specimen: there might already be a matching specimen, but it must be me
                the_obj = match_obj.get()
                if the_obj.pk != self.pk:
                    raise ValidationError("Vial should be unique for a given expedition")

        if not settings.DISABLE_MNHN_UNIQUENESS_VALIDATION:  # Unique, but only if not null
            self._check_field_unique_if_not_null('mnhn_number', "MNHN number must be unique (if not null)")

        self._check_field_unique_if_not_null('sequence_name', "Sequence name number must be unique (if not null)")

        if self.isotope_percentN and self.isotope_percentC:
            if self.isotope_percentC < self.isotope_percentN:
                raise ValidationError("Isotope: %C must be < %N")

    def save(self, *args, **kwargs):
        self.full_clean()  # We want our custom clean method to be called at save()
        return super(Specimen, self).save(*args, **kwargs)

    def __str__(self):
        return "Specimen #{specimen_id}".format(specimen_id=self.specimen_id)

    class Meta:
        ordering = ['specimen_id']


class SpecimenPicture(models.Model):
    image = models.ImageField(upload_to='specimen_pictures')
    high_interest = models.BooleanField("High resolution/species representative")
    specimen = models.ForeignKey(Specimen, on_delete=models.CASCADE)
