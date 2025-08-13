from django.contrib import admin
from .models import Mood, Landmark, Station, LandmarkComment, UserLocal, LandmarkImage


# Inline para subir imágenes secundarias en Landmark
class LandmarkImageInline(admin.TabularInline):
    model = LandmarkImage
    extra = 1
    fields = ["image", "description"]


@admin.register(Mood)
class MoodAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Landmark)
class LandmarkAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "emotions_display", "moods_display"]
    list_filter = ["moods"]
    search_fields = ["name", "code", "description", "emotions"]
    inlines = [LandmarkImageInline]

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
    filter_horizontal = ["landmarks"]

    def emotions_display(self, obj):
        return obj.emotions or "(ninguna)"

    emotions_display.short_description = "Emociones"

    def landmarks_count(self, obj):
        return obj.landmarks.count()

    landmarks_count.short_description = "Cantidad de Hitos"


@admin.register(LandmarkComment)
class LandmarkCommentAdmin(admin.ModelAdmin):
    list_display = ["author_name", "landmark", "short_description", "created_at"]
    list_filter = ["created_at", "landmark"]
    search_fields = ["author_name", "description", "landmark__name"]

    def short_description(self, obj):
        return obj.description[:50] + ("..." if len(obj.description) > 50 else "")

    short_description.short_description = "Descripción"


@admin.register(UserLocal)
class UserLocalAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "created_at"]
    search_fields = ["id", "name"]
    ordering = ["-created_at"]
