from django.contrib.gis.db import models

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
    location = models.PointField()
    depth = models.IntegerField(blank=True, null=True)
    identified_by = models.ForeignKey(Person)
    location = models.ForeignKey(SpecimenLocation)
    comment = models.TextField(blank=True, null=True)


