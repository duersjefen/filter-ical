# Multi-stage build for iCal Viewer Clojure Backend
FROM clojure:temurin-17-tools-deps-jammy

WORKDIR /app

# Copy backend deps file first for better caching
COPY backend/deps.edn ./

# Download dependencies
RUN clojure -P

# Copy backend source code
COPY backend/src/ ./src/
COPY backend/test/ ./test/

# Create data directory for persistence
RUN mkdir -p ./data

# Expose the port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:3000/ || exit 1

# Run the application
CMD ["clojure", "-M", "-m", "app.server"]