FROM python:3.12.1-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    pkg-config \
    python3-dev 

RUN apt-get install --assume-yes git

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . ./

# Make entrypoints executable
RUN chmod +x /app/deployment/server-entrypoint.sh && \
    chmod +x /app/deployment/worker-entrypoint.sh

CMD sleep 3

CMD [ "/app/deployment/server-entrypoint.sh" ]