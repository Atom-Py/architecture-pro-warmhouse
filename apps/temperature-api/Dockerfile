FROM golang:1.22-alpine AS build-stage
ENV CGO_ENABLED=0 \
  GOOS=linux
WORKDIR /src
COPY go.mod go.sum ./
RUN --mount=type=cache,target=/go/pkg/mod go mod download
COPY main.go ./
RUN --mount=type=cache,target=/go/pkg/mod \
  --mount=type=cache,target=/root/.cache/go-build \
  go build -ldflags='-s -w' -o /out/temperature-api


FROM alpine:latest AS app-stage
ENV GIN_MODE=release
RUN apk --no-cache add ca-certificates tzdata \
  && adduser -S -u 1000 app
WORKDIR /app
COPY --from=build-stage /out/temperature-api ./
EXPOSE 8081
USER app
CMD ["./temperature-api"]
