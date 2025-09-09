# Build stage for ClojureScript
FROM node:18-alpine AS build

WORKDIR /app

# Install shadow-cljs globally
RUN npm install -g shadow-cljs

# Copy project files
COPY shadow-cljs.edn .
COPY package.json* ./

# Install npm dependencies if package.json exists
RUN if [ -f package.json ]; then npm install; fi

# Copy source code
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