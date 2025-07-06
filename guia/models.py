from django.contrib.gis.db import models as geomodels
from django.db import models


class Mood(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Landmark(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, default="default", unique=True)
    description = models.TextField(blank=True)
    emotions = models.TextField(blank=True)
    moods = models.ManyToManyField(Mood, blank=True)
    geom = geomodels.PointField(srid=4326)
    main_image = models.ImageField(upload_to="landmarks/main/", null=True, blank=True)

    def __str__(self):
        return self.name


class LandmarkImage(models.Model):
    landmark = models.ForeignKey(
        Landmark, related_name="secondary_images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="landmarks/secondary/")
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Imagen de {self.landmark.name}"


class Station(models.Model):
    name = models.CharField(max_length=100, unique=True)
    emotions = models.TextField(blank=True)

    # Zona de cobertura en vez de centro y radio
    area = geomodels.PolygonField(srid=4326)

    # Hitos asociados
    landmarks = models.ManyToManyField(Landmark, related_name="stations")

    def __str__(self):
        return self.name


class UserLocal(models.Model):
    id = models.CharField(
        primary_key=True, max_length=100
    )  # UUID o timestamp desde Flutter
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class LandmarkComment(models.Model):
    author_id = models.CharField(max_length=100)
    author_name = models.CharField(max_length=100)
    landmark = models.ForeignKey(
        Landmark, on_delete=models.CASCADE, related_name="comments"
    )
    description = models.TextField()
    emotions = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author_name} sobre {self.landmark.code}"
