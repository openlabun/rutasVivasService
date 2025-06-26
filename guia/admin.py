from django.contrib import admin
from .models import Mood, Landmark, Station


@admin.register(Mood)
class MoodAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Landmark)
class LandmarkAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "emotions_display", "moods_display"]
    list_filter = ["moods"]
    search_fields = ["name", "code", "description", "emotions"]

    def emotions_display(self, obj):
        return obj.emotions or "(ninguna)"

    emotions_display.short_description = "Emociones"

    def moods_display(self, obj):
        return ", ".join([m.name for m in obj.moods.all()])

    moods_display.short_description = "Moods"


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ["name", "emotions_display", "landmarks_count"]
    search_fields = ["name", "emotions"]
    filter_horizontal = ["landmarks"]  # Mejora el widget para seleccionar muchos hitos

    def emotions_display(self, obj):
        return obj.emotions or "(ninguna)"

    emotions_display.short_description = "Emociones"

    def landmarks_count(self, obj):
        return obj.landmarks.count()

    landmarks_count.short_description = "Cantidad de Hitos"
