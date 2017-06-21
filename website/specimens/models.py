from django.contrib.gis.db import models
from django.contrib.postgres.fields import FloatRangeField

UNKNOWN_STATION_NAME = '<Unknown>'  # Sometimes we need a "fake" station to link Specimen to Expedition

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
    scientific_name = models.CharField(max_length=100)
    coords = models.PointField("Coordinates", blank=True, null=True)
    depth = FloatRangeField(blank=True, null=True, help_text="Unit: meters.")
    identified_by = models.ForeignKey(Person)
    specimen_location = models.ForeignKey(SpecimenLocation)
    fixation = models.ForeignKey(Fixation, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    station = models.ForeignKey(Station)

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
        return "Specimen #{specimen_id} ({scientific_name})".format(specimen_id=self.specimen_id,
                                                                    scientific_name=self.scientific_name)


class SpecimenPicture(models.Model):
    image = models.ImageField(upload_to='specimen_pictures')
    high_interest = models.BooleanField("High resolution/species representative")
    specimen = models.ForeignKey(Specimen)


