# Përdor Python 3.10 (jo 3.13 që ka problem me imghdr)
FROM python:3.10-slim

# Vendosi direktorët e punës
WORKDIR /app

# Kopjo skedarët në imazh
COPY . /app

# Instalo varësitë
RUN pip install --no-cache-dir -r requirements.txt

# Startimi i aplikacionit
CMD ["python", "main.py"]
