# syntax=docker/dockerfile:1
FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLOCI_ENDPOINT=http://floci:4566 \
    AWS_DEFAULT_REGION=us-east-1 \
    AWS_ACCESS_KEY_ID=test \
    AWS_SECRET_ACCESS_KEY=test \
    FLOCI_OBJECT_BUCKET=floci-cloud-lab-local-objects \
    FLOCI_METADATA_TABLE=floci-cloud-lab-local-metadata

WORKDIR /app

COPY requirements-dev.txt ./requirements-dev.txt
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements-dev.txt

COPY app ./app
COPY scripts ./scripts
COPY docs ./docs
COPY README.md ./README.md

EXPOSE 8080

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=5 \
  CMD python -c "import json, urllib.request; r=urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=2); assert r.status == 200; json.loads(r.read().decode())"

CMD ["python", "-m", "app.backend.local_server", "--host", "0.0.0.0", "--port", "8080"]
