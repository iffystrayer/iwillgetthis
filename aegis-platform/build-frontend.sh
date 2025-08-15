#!/bin/bash

# Build script for Aegis frontend with proper environment variables
# This ensures VITE variables are correctly passed to Docker build

set -e

# Source the .env file to get the variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Export the specific VITE variables needed for build
export VITE_API_URL=${VITE_API_URL:-http://localhost:30641/api/v1}
export VITE_USE_MOCK_API=${VITE_USE_MOCK_API:-false}
export VITE_ENVIRONMENT=${VITE_ENVIRONMENT:-production}

echo "Building frontend with environment variables:"
echo "VITE_API_URL=$VITE_API_URL"
echo "VITE_USE_MOCK_API=$VITE_USE_MOCK_API"  
echo "VITE_ENVIRONMENT=$VITE_ENVIRONMENT"

# Build the frontend container
docker-compose -f docker/docker-compose.yml build frontend --no-cache

echo "Frontend build completed successfully!"