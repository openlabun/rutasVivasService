from django.urls import path
from .views import EmotionalRouteView, landmarks_geojson

urlpatterns = [
    path('api/emotional-route/', EmotionalRouteView.as_view(), name='emotional_route'),
    path('api/landmarks.geojson/', landmarks_geojson, name='landmarks_geojson'),
]
