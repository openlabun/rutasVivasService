import requests
from django.contrib.gis.geos import Point
from rest_framework.parsers import MultiPartParser, FormParser

from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from guia.models import Landmark, LandmarkComment, Mood, Station, UserLocal
from guia.serializers import (
    LandmarkSerializer,
    LandmarkImageSerializer,
    StationSerializer,
    UserLocalSerializer,
    LandmarkCommentSerializer,
)


class LandmarkBulkCreateView(APIView):
    def post(self, request):
        if not isinstance(request.data, list):
            return Response({"error": "Se espera una lista de objetos"}, status=400)

        serializer = LandmarkSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class LandmarkImageUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, landmark_id):
        try:
            landmark = Landmark.objects.get(pk=landmark_id)
        except Landmark.DoesNotExist:
            return Response({"error": "Landmark no encontrado"}, status=404)

        serializer = LandmarkImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(landmark=landmark)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class EmotionalRouteView(APIView):
    def post(self, request):
        mood = request.data.get("mood")
        lat = request.data.get("latitude")
        lon = request.data.get("longitude")
        minutes = int(request.data.get("minutes", 10))

        if not mood or not lat or not lon:
            return Response({"error": "Datos incompletos"}, status=400)

        start = Point(float(lon), float(lat))

        mood_obj = Mood.objects.filter(name__iexact=mood).first()
        if not mood_obj:
            return Response({"error": "Mood no válido"}, status=404)

        # Buscar landmarks que tengan ese mood y ordenarlos por cercanía
        landmarks = Landmark.objects.filter(moods=mood_obj)
        landmarks = sorted(landmarks, key=lambda l: l.geom.distance(start))

        points = [start] + [l.geom for l in landmarks]
        names = ["Inicio"] + [l.name for l in landmarks]

        tramos = []
        total_duration_min = 0.0
        total_distance_km = 0.0

        for i in range(len(points) - 1):
            from_point = points[i]
            to_point = points[i + 1]

            osrm_url = (
                f"http://osrm_server:5000/route/v1/foot/"
                f"{from_point.x},{from_point.y};{to_point.x},{to_point.y}"
            )
            res = requests.get(
                osrm_url, params={"overview": "full", "geometries": "geojson"}
            )

            if res.status_code != 200:
                continue

            route = res.json()["routes"][0]
            tramo_duration_min = route["duration"] / 60
            tramo_distance_km = route["distance"] / 1000

            # ⚠️ Detener si agregar este tramo supera el tiempo disponible
            if total_duration_min + tramo_duration_min > minutes:
                break

            tramos.append(
                {
                    "from": names[i],
                    "to": names[i + 1],
                    "geometry": route["geometry"],
                    "distance_km": round(tramo_distance_km, 2),
                    "duration_min": round(tramo_duration_min, 1),
                }
            )

            total_duration_min += tramo_duration_min
            total_distance_km += tramo_distance_km

        return Response(
            {
                "tramos": tramos,
                "total_distance_km": round(total_distance_km, 2),
                "total_duration_min": round(total_duration_min, 1),
            }
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def landmarks_geojson(request):
    features = []

    landmarks = Landmark.objects.all()

    for landmark in landmarks:
        if not landmark.geom:
            continue

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [landmark.geom.x, landmark.geom.y],
            },
            "properties": {
                "id": landmark.id,
                "name": landmark.name,
                "description": landmark.description,
                "main_image": landmark.main_image.url if landmark.main_image else None,
                "secondary_images": [
                    {
                        "id": img.id,
                        "image": img.image.url,
                        "description": img.description,
                    }
                    for img in landmark.secondary_images.all()
                ],
                "code": landmark.code,
                "emotions": landmark.emotions,  # texto plano separado por comas
                "moods": [m.name for m in landmark.moods.all()],  # lista de moods
            },
        }
        features.append(feature)

    return Response({"type": "FeatureCollection", "features": features})


class StationListView(generics.ListAPIView):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class StationCreateView(generics.CreateAPIView):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class UserLocalCreateView(generics.CreateAPIView):
    queryset = UserLocal.objects.all()
    serializer_class = UserLocalSerializer


class LandmarkCommentCreateView(generics.CreateAPIView):
    queryset = LandmarkComment.objects.all()
    serializer_class = LandmarkCommentSerializer
