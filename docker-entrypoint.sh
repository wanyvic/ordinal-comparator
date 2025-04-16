#!/bin/sh
set -e

echo "Starting Ordinal Comparator container..."

# Create logs directory if it doesn't exist
echo "Setting up log directory..."
mkdir -p /app/logs

# Ensure correct permissions
echo "Setting permissions for log directory..."
chmod 755 /app/logs

echo "Environment variables:"
echo "PRIMARY_ENDPOINT: ${PRIMARY_ENDPOINT}"
echo "SECONDARY_ENDPOINT: ${SECONDARY_ENDPOINT}"
echo "PROTOCOL: ${PROTOCOL}"
echo "CHAIN: ${CHAIN}"
echo "THREADS: ${THREADS}"
echo "LOG_LEVEL: ${LOG_LEVEL}"
echo "START_BLOCK: ${START_BLOCK}"
echo "END_BLOCK: ${END_BLOCK}"

echo "Starting application with command: $@"
# Execute the main command with output visible in docker logs
exec "$@" 