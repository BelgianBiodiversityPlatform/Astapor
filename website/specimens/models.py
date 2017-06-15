from django.contrib.gis.db import models
from django.contrib.postgres.fields import FloatRangeField

class Person(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    class Meta:
        unique_together = ("first_name", "last_name")

class SpecimenLocation(models.Model):
    name = models.CharField(max_length=100)

class Specimen(models.Model):
    specimen_id = models.IntegerField(unique=True)  # ID from the lab, not Django's PK
    scientific_name = models.CharField(max_length=100)
    coords = models.PointField(blank=True, null=True)
    depth = FloatRangeField(blank=True, null=True)  # Waiting confirmation for unit and integer/float
    identified_by = models.ForeignKey(Person)
    specimen_location = models.ForeignKey(SpecimenLocation)
    comment = models.TextField(blank=True, null=True)


