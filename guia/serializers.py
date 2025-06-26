from rest_framework import serializers
from guia.models import Landmark, Mood, LandmarkImage, Station
from django.contrib.gis.geos import Point, Polygon


class LandmarkSerializer(serializers.ModelSerializer):
    moods = serializers.SlugRelatedField(
        many=True, slug_field="name", queryset=Mood.objects.all()
    )
    main_image = serializers.ImageField(required=False, allow_null=True)

    # Si quieres mostrar imágenes secundarias también
    secondary_images = serializers.SerializerMethodField()

    class Meta:
        model = Landmark
        fields = [
            "name",
            "code",
            "description",
            "emotions",
            "geom",
            "moods",
            "main_image",
            "secondary_images",
        ]
        extra_kwargs = {"secondary_images": {"read_only": True}}

    def get_secondary_images(self, obj):
        return [
            {
                "id": img.id,
                "image": self.context["request"].build_absolute_uri(img.image.url),
                "description": img.description,
            }
            for img in obj.secondary_images.all()
        ]

    def create(self, validated_data):
        moods_data = validated_data.pop("moods", [])
        geom_data = validated_data.pop("geom")

        # Procesar coordenadas del punto
        point = Point(geom_data["coordinates"][0], geom_data["coordinates"][1])

        # Crear el Landmark
        landmark = Landmark.objects.create(geom=point, **validated_data)
        landmark.moods.set(moods_data)

        return landmark

    def create_bulk(self, validated_data_list):
        return [self.create(data) for data in validated_data_list]


class LandmarkImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandmarkImage
        fields = ["id", "landmark", "image", "description"]


class StationSerializer(serializers.ModelSerializer):
    landmarks = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Landmark.objects.all()
    )

    class Meta:
        model = Station
        fields = ["id", "name", "emotions", "area", "landmarks"]

    def create(self, validated_data):
        landmarks_data = validated_data.pop("landmarks")
        area_geojson = validated_data.pop("area")

        # Convertir dict GeoJSON a Polygon
        coords = area_geojson["coordinates"][0]
        polygon = Polygon(coords)

        station = Station.objects.create(area=polygon, **validated_data)
        station.landmarks.set(landmarks_data)
        return station
