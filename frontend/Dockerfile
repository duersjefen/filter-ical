# Multi-stage build for Vue 3 frontend
# Stage 1: Build application
FROM node:22-alpine AS builder

WORKDIR /app

# Cache-busting: Force rebuild when source code changes
# This arg should be set to git commit hash during build
ARG GIT_COMMIT=unknown
RUN echo "Building from commit: $GIT_COMMIT"

# Copy package files first (cache layer)
COPY package*.json ./

# Install dependencies (including dev dependencies needed for build)
RUN npm ci --prefer-offline --no-audit

# Copy source code
COPY . .

# Accept API base URL as build argument (empty string means relative URLs)
ARG VITE_API_BASE_URL=""
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

# Build the application
RUN npm run build

# Stage 2: Production runtime with nginx
# Using nginx-brotli image for better compression (20-30% smaller than gzip)
# v1.28.0 is based on nginx 1.28.0 stable + brotli module
FROM fholzer/nginx-brotli:v1.28.0

# Cache-busting: Inherit GIT_COMMIT from builder stage
ARG GIT_COMMIT=unknown
RUN echo "Deploying commit: $GIT_COMMIT"

# Install curl for health checks (Alpine doesn't include it by default)
RUN apk add --no-cache curl

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built app from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Configure permissions for non-root nginx user
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/run/nginx.pid

# Run as non-root user
USER nginx

# Expose port
EXPOSE 80

# Health check - curl the /health endpoint every 10s
# Start checking after 5s (give nginx time to start)
# Timeout after 5s, allow 3 retries before marking unhealthy
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Base image already has ENTRYPOINT ["nginx"] and CMD ["-g", "daemon off;"]
# No need to override - using base image's CMD