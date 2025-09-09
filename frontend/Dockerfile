# Development stage - just serve the files with nginx
FROM nginx:alpine

# Copy static files
COPY resources/public /usr/share/nginx/html

# Custom nginx config for SPA
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]