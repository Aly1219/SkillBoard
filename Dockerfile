FROM python:3.11-slim

WORKDIR /app

# Copier uniquement les dépendances en premier pour profiter du cache Docker.
# Tant que requirements-docker.txt ne change pas, pip install n'est pas rejoué.
COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copier le reste du code source
COPY . .

# Créer le répertoire de la base de données et un utilisateur non-root
RUN mkdir -p /app/instance \
    && adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 5000

CMD ["python", "run.py"]