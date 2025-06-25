import json
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from guia.models import Emotion, Landmark

GEO_DATA = [
    {
        "name": "Ceiba Roja",
        "coords": (-74.84999478518809, 11.019054643140194),
        "emotion": "tranqui"
    },
    {
        "name": "Fauna del Bosque Seco Tropical",
        "coords": (-74.85000713425129, 11.019424108257311),
        "emotion": "recargado"
    },
    {
        "name": "Palma Real",
        "coords": (-74.85074238724663, 11.01960690780578),
        "emotion": "tranqui"
    },
    {
        "name": "Aistonia",
        "coords": (-74.85085191153578, 11.019773626527211),
        "emotion": "neutro"
    },
    {
        "name": "Bonga: Árbol de la resiliencia",
        "coords": (-74.85145269784371, 11.019884429154274),
        "emotion": "recargado"
    },
]

class Command(BaseCommand):
    help = 'Poblar la base de datos con emociones y landmarks'

    def handle(self, *args, **kwargs):
        # Crear emociones
        for emo in ["tranqui", "neutro", "recargado"]:
            Emotion.objects.get_or_create(name=emo)

        self.stdout.write(self.style.SUCCESS('Emociones creadas.'))

        # Crear landmarks
        for item in GEO_DATA:
            emotion = Emotion.objects.get(name=item["emotion"])
            Landmark.objects.create(
                name=item["name"],
                emotion=emotion,
                description=f"Punto con emoción {item['emotion']}",
                geom=Point(*item["coords"])
            )

        self.stdout.write(self.style.SUCCESS('Landmarks cargados con éxito.'))
