# Build stage for ClojureScript with optimized layer caching
FROM node:18-alpine AS build

WORKDIR /app

# Install system dependencies (cached independently)
RUN apk add --no-cache openjdk17-jre

# Install shadow-cljs globally (cached independently)
RUN npm install -g shadow-cljs

# Copy dependency files first for better caching
COPY package.json* ./
COPY shadow-cljs.edn .

# Install npm dependencies (cached when package.json unchanged)
RUN if [ -f package.json ]; then npm install; fi

# Copy source code (changes more frequently, separate layer)
COPY src/ src/
COPY resources/ resources/

# Build ClojureScript for production
RUN shadow-cljs release app

# Production stage - serve built files with nginx
FROM nginx:alpine

# Copy built static files from build stage
COPY --from=build /app/resources/public /usr/share/nginx/html

# Copy custom nginx config for SPA
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]