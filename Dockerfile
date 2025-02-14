FROM python:3.10-slim

LABEL maintainer="laoning"
LABEL version="1.0.0"
LABEL description="Synology Chat Bot with AI integration"

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV ENVIRONMENT=production

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

COPY . /app/

EXPOSE 8008

CMD ["gunicorn", "--bind", "0.0.0.0:8008", "--workers", "4", "--timeout", "120", "app:app"]