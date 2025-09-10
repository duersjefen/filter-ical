FROM clojure:temurin-17-tools-deps-jammy

WORKDIR /app

# Copy dependency file first for optimal caching (changes less frequently)
COPY deps.edn .

# Download and cache dependencies (expensive operation, cached when deps.edn unchanged)
RUN clojure -P

# Copy data files (changes infrequently, separate layer)
COPY data/ data/

# Copy test files (changes less frequently than src)
COPY test/ test/

# Copy source code last (changes most frequently)
COPY src/ src/

EXPOSE 3000

CMD ["clojure", "-M:run"]