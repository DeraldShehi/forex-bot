# Dockerfile

# Bazë me python 3.10.4 slim version (më pak hapësirë)
FROM python:3.10.4-slim

# Vendos folderin e punës
WORKDIR /app

# Kopjo vetëm requirements për të përshpejtuar build-in
COPY requirements.txt .

# Instalimi i dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Kopjo gjithë kodin e projektit
COPY . .

# Komanda që do të startojë boti yt
CMD ["python3", "main.py"]
