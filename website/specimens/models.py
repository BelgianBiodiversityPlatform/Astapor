from django.contrib.gis.db import models
from django.contrib.postgres.fields import FloatRangeField
from django.core.exceptions import ObjectDoesNotExist

from mptt.models import MPTTModel, TreeForeignKey

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
    rank = models.ForeignKey(TaxonRank)
    status = models.ForeignKey(TaxonStatus, null=True, blank=True)
    aphia_id = models.IntegerField(null=True, blank=True)
    authority = models.CharField(max_length=100, null=True, blank=True)

    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

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


class Station(models.Model):
    name = models.CharField(max_length=100)
    expedition = models.ForeignKey(Expedition)
    # It may be interesting to add a location (point, polygon or line) for the station itself, but for now we keep the
    # coordinates as a specimen attribute (when sampling we generally try to set the lat/lon for the specimen as precisely
    # as possible, sometimes more than the station)
    def __str__(self):
        return "{name} (from exp. {exp_name})".format(name=self.name, exp_name=self.expedition)


class Specimen(models.Model):
    specimen_id = models.IntegerField(unique=True)  # ID from the lab, not Django's PK
    initial_scientific_name = models.CharField(max_length=100)
    taxon = models.ForeignKey(Taxon, null=True, blank=True)
    coords = models.PointField("Coordinates", blank=True, null=True)
    depth = FloatRangeField(blank=True, null=True, help_text="Unit: meters.")
    identified_by = models.ForeignKey(Person)
    specimen_location = models.ForeignKey(SpecimenLocation)
    fixation = models.ForeignKey(Fixation, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    station = models.ForeignKey(Station)

    def has_pictures(self):
        return self.specimenpicture_set.count() > 0

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

    def __str__(self):
        return "Specimen #{specimen_id}".format(specimen_id=self.specimen_id)

    class Meta:
        ordering = ['specimen_id']


class SpecimenPicture(models.Model):
    image = models.ImageField(upload_to='specimen_pictures')
    high_interest = models.BooleanField("High resolution/species representative")
    specimen = models.ForeignKey(Specimen)


