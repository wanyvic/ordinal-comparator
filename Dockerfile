FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates openssl && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir .

ENTRYPOINT ["ordinal-comparator"]