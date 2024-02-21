FROM python:3.10.12-alpine3.18

WORKDIR /app

COPY requirements.txt .

RUN apk add --no-cache mariadb-dev build-base && \
    pip install --no-cache-dir -r requirements.txt && apk del build-base

COPY . .

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
 CMD curl -f http://localhost:5000/health || exit 1

ENTRYPOINT ["python", "server.py"]