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

# Install curl for health checks (Alpine doesn't include it by default)
RUN apk add --no-cache curl

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built app from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Expose port
EXPOSE 80

# Health check - curl the /health endpoint every 10s
# Start checking after 5s (give nginx time to start)
# Timeout after 5s, allow 3 retries before marking unhealthy
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Reset entrypoint from base image (fholzer/nginx-brotli has ENTRYPOINT [nginx])
# Without this, Docker would run: nginx nginx -g daemon off; (duplicate nginx)
ENTRYPOINT []

# Start nginx
CMD ["nginx", "-g", "daemon off;"]