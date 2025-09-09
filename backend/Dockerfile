FROM clojure:temurin-17-tools-deps-jammy

WORKDIR /app

# Copy deps file first for better caching
COPY deps.edn .

# Download dependencies
RUN clojure -P

# Copy source code
COPY src/ src/
COPY test/ test/
COPY data/ data/

EXPOSE 3000

CMD ["clojure", "-M:run"]