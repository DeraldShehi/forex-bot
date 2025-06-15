# Përdor Python 3.10
FROM python:3.10-slim

# Vendos direktorinë e punës brenda containerit
WORKDIR /app

# Kopjo të gjitha file nga repo në imazhin e dockerit
COPY . .

# Instalo varësitë
RUN pip install --no-cache-dir -r requirements.txt

# Komanda për të startuar botin
CMD ["python", "main.py"]
