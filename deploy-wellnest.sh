#!/bin/bash
set -e

# Define your project folder path
STACK_DIR="/home/azureuser/careyogi-stack"

echo "==== Starting Deployment: $(date) ===="

# Force switch directory using the absolute path
cd "$STACK_DIR"

# Use absolute path to the docker compose binary
/usr/bin/docker compose pull
/usr/bin/docker compose up -d

echo "Listing newly created containers:"
/usr/bin/docker compose ps

echo "Running Frappe Multi-Tenant Migrations..."
/usr/bin/docker compose exec -T backend bench --site careyogis.local migrate

echo "==== Deployment Completed Successfully ===="
