from django.contrib.gis.db import models

class Specimen(models.Model):
    location = models.PointField()
