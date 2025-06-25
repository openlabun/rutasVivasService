from django.contrib.gis.db import models as geomodels
from django.db import models

class Emotion(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Landmark(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, blank=True, null=True) 
    description = models.TextField(blank=True)
    emotion = models.ForeignKey(Emotion, on_delete=models.CASCADE)
    geom = geomodels.PointField(srid=4326)  # Coordenadas en lat/lon (WGS84)

    def __str__(self):
        return self.name
