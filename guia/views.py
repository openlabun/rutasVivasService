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

        # Filtra y ordena todos los hitos compatibles por cercanía al punto de inicio
        all_landmarks = list(Landmark.objects.filter(moods=mood_obj).order_by("geom"))

        if not all_landmarks:
            return Response({"error": "No hay hitos para este mood"}, status=404)

        coords = [f"{lon},{lat}"]  # Coordenadas iniciales
        visited = []
        total_duration = 0
        total_distance = 0

        for landmark in all_landmarks:
            test_coords = coords + [f"{landmark.geom.x},{landmark.geom.y}"]
            osrm_url = f"http://osrm_server:5000/route/v1/foot/" + ";".join(test_coords)

            res = requests.get(
                osrm_url, params={"overview": "full", "geometries": "geojson"}
            )
            if res.status_code != 200:
                continue

            data = res.json()["routes"][0]
            duration = data["duration"]
            distance = data["distance"]

            if duration <= minutes * 60:
                coords.append(f"{landmark.geom.x},{landmark.geom.y}")
                visited.append(landmark)
                total_duration = duration
                total_distance = distance
            else:
                break  # Ya no caben más hitos

        if not visited:
            return Response(
                {"error": "No se encontró una ruta dentro del tiempo indicado"},
                status=404,
            )

        return Response(
            {
                "route": data["geometry"],
                "distance_km": total_distance / 1000,
                "duration_min": total_duration / 60,
                "visited": [v.name for v in visited],
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
