docker build -t ghcr.io/smck83/test-direct-smtp-relay . --no-cache

docker run -it -p 8000:8000 ghcr.io/smck83/test-direct-smtp-relay