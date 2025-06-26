#!/bin/bash

echo "⏳ Esperando a que la base de datos esté disponible..."
while ! nc -z db 5432; do
  sleep 1
done

echo "✅ Generando y ejecutando migraciones..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput


echo "👤 Verificando superusuario..."
echo "from django.contrib.auth import get_user_model; \
User = get_user_model(); \
User.objects.filter(username='${DJANGO_SUPERUSER_USERNAME}').exists() or \
User.objects.create_superuser('${DJANGO_SUPERUSER_USERNAME}', '${DJANGO_SUPERUSER_EMAIL}', '${DJANGO_SUPERUSER_PASSWORD}')" \
| python manage.py shell

echo "🚀 Iniciando servidor Django..."
exec python manage.py runserver 0.0.0.0:8000
