from django.urls import path
from .views import (
    EmotionalRouteView,
    LandmarkBulkCreateView,
    LandmarkCommentCreateView,
    StationCreateView,
    UserLocalCreateView,
    landmarks_geojson,
    LandmarkImageUploadView,
    StationListView,
)

urlpatterns = [
    path("api/emotional-route/", EmotionalRouteView.as_view(), name="emotional_route"),
    path("api/landmarks.geojson/", landmarks_geojson, name="landmarks_geojson"),
    path(
        "api/landmarks/bulk/",
        LandmarkBulkCreateView.as_view(),
        name="landmark-bulk-create",
    ),
    path(
        "landmarks/<int:landmark_id>/upload-image/",
        LandmarkImageUploadView.as_view(),
        name="upload-secondary-image",
    ),
    path("stations/", StationListView.as_view(), name="station-list"),
    path("stations/create/", StationCreateView.as_view(), name="station-create"),
    path("api/user-local/", UserLocalCreateView.as_view(), name="create_user_local"),
    path(
        "api/comments/create/",
        LandmarkCommentCreateView.as_view(),
        name="create-comment",
    ),
]
