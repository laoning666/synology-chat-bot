FROM python:3.10-slim

LABEL maintainer="laoning"
LABEL version="1.0.0"
LABEL description="Synology Chat Bot with AI integration"

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV ENVIRONMENT=production

COPY . /app/
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8008
CMD ["python", "app.py"]