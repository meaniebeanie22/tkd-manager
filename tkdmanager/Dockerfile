FROM python:3.12.1-slim

ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    pkg-config \
    libcairo2-dev \
    python3-dev \
    apt-get install --assume-yes git

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . ./

# Collect static files
RUN python manage.py collectstatic --noinput

CMD sleep 3 && gunicorn tkdmanager.wsgi --log-file -