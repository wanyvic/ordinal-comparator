FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates openssl && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir .

# Create logs directory
RUN mkdir -p /app/logs && chmod 755 /app/logs

# Copy entrypoint script and make it executable
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Default command if no command is provided
CMD ["ordinal-comparator", "--help"]