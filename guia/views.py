from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from guia.models import Emotion, Landmark
from django.contrib.gis.geos import Point
import requests

class EmotionalRouteView(APIView):
    def post(self, request):
        mood = request.data.get('mood')
        lat = request.data.get('latitude')
        lon = request.data.get('longitude')
        minutes = int(request.data.get('minutes', 10))

        if not mood or not lat or not lon:
            return Response({"error": "Datos incompletos"}, status=400)

        # Crear punto de inicio
        start = Point(float(lon), float(lat))

        # Obtener emoción
        emotion = Emotion.objects.filter(name__iexact=mood).first()
        if not emotion:
            return Response({"error": "Emoción no válida"}, status=404)

        # Buscar landmarks con esa emoción (limitado a los más cercanos por ahora)
        landmarks = Landmark.objects.filter(emotion=emotion)
        close_points = sorted(
            landmarks, key=lambda l: l.geom.distance(start)
        )[:3]  # más adelante esto será por tiempo, no solo distancia

        coords = [f"{lon},{lat}"] + [f"{p.geom.x},{p.geom.y}" for p in close_points]

        # Llamar a OSRM
        osrm_url = f"http://localhost:8080/route/v1/foot/" + ";".join(coords)
        res = requests.get(osrm_url, params={
            'overview': 'full',
            'geometries': 'geojson'
        })

        if res.status_code != 200:
            return Response({"error": "No se pudo conectar con OSRM"}, status=500)

        route_data = res.json()['routes'][0]

        return Response({
            "route": route_data['geometry'],
            "distance_km": route_data['distance'] / 1000,
            "duration_min": route_data['duration'] / 60,
            "visited": [p.name for p in close_points]
        })
    


@api_view(['GET'])
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
                "coordinates": [landmark.geom.x, landmark.geom.y]
            },
            "properties": {
                "name": landmark.name,
                "code": landmark.code,
                "emotion": landmark.emotion.name if landmark.emotion else None
            }
        }
        features.append(feature)

    return Response({
        "type": "FeatureCollection",
        "features": features
    })

