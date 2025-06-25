from django.contrib import admin

# Register your models here.
from .models import Emotion, Landmark

@admin.register(Emotion)
class EmotionAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Landmark)
class LandmarkAdmin(admin.ModelAdmin):
    list_display = ['name','code', 'emotion']
    list_filter = ['emotion']
    search_fields = ['name', 'code', 'description']