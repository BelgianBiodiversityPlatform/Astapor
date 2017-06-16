from django.contrib.gis.db import models
from django.contrib.postgres.fields import FloatRangeField

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

class Specimen(models.Model):
    specimen_id = models.IntegerField(unique=True)  # ID from the lab, not Django's PK
    scientific_name = models.CharField(max_length=100)
    coords = models.PointField("Coordinates", blank=True, null=True)
    depth = FloatRangeField(blank=True, null=True, help_text="Unit: meters.")
    identified_by = models.ForeignKey(Person, blank=True, null=True)
    specimen_location = models.ForeignKey(SpecimenLocation)
    fixation = models.ForeignKey(Fixation, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)


