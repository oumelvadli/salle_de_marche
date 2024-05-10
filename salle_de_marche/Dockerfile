# Utiliser l'image Python officielle en tant que base
FROM python:3

# Définir l'environnement de travail
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Créer et définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier requirements.txt dans le répertoire de travail
COPY requirements.txt /app/

# Installer les dépendances Python spécifiées dans le fichier requirements.txt
RUN pip install  -r requirements.txt

# Copier le reste du code source dans le répertoire de travail
# COPY . /app/

# Exposer le port 8000 pour le serveur web
EXPOSE 8000

# Commande pour démarrer le serveur Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
