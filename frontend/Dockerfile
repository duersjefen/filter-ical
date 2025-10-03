# Frontend Dockerfile for Vue 3 + nginx
FROM node:22-alpine AS build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (including dev dependencies needed for build)
RUN npm ci

# Copy source code
COPY . .

# Accept API base URL as build argument (empty string means relative URLs)
ARG VITE_API_BASE_URL=""
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

# Build the application
RUN npm run build

# Production stage
# Using nginx-brotli image for better compression (20-30% smaller than gzip)
# v1.28.0 is based on nginx 1.28.0 stable + brotli module
FROM fholzer/nginx-brotli:v1.28.0

# Install curl for health checks and gettext for envsubst (Alpine doesn't include them by default)
RUN apk add --no-cache curl gettext

# Copy nginx configuration template
COPY nginx.conf /etc/nginx/nginx.conf.template

# Copy built app from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Create startup script to substitute environment variables in nginx config
RUN echo '#!/bin/sh' > /docker-entrypoint.sh && \
    echo 'set -e' >> /docker-entrypoint.sh && \
    echo 'echo "🔧 Configuring nginx with BACKEND_HOST=${BACKEND_HOST:-backend}"' >> /docker-entrypoint.sh && \
    echo 'export BACKEND_HOST=${BACKEND_HOST:-backend}' >> /docker-entrypoint.sh && \
    echo 'envsubst '"'"'$BACKEND_HOST'"'"' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf' >> /docker-entrypoint.sh && \
    echo 'echo "✅ nginx configuration ready"' >> /docker-entrypoint.sh && \
    echo 'exec "$@"' >> /docker-entrypoint.sh && \
    chmod +x /docker-entrypoint.sh

# Expose port
EXPOSE 80

# Health check - curl the /health endpoint every 10s
# Start checking after 5s (give nginx time to start)
# Timeout after 5s, allow 3 retries before marking unhealthy
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Use custom entrypoint to substitute environment variables before starting nginx
ENTRYPOINT ["/docker-entrypoint.sh"]

# Start nginx
CMD ["nginx", "-g", "daemon off;"]