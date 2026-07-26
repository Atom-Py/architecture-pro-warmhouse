FROM gradle:8.14-jdk21 AS build-stage
WORKDIR /src
COPY settings.gradle.kts build.gradle.kts ./
COPY gradle/ gradle/
RUN --mount=type=cache,target=/home/gradle/.gradle gradle --no-daemon dependencies > /dev/null || true
COPY src/ src/
RUN --mount=type=cache,target=/home/gradle/.gradle gradle --no-daemon installDist


FROM eclipse-temurin:21-jre-alpine AS app-stage
RUN apk --no-cache add curl \
  && adduser -S -u 1000 app
WORKDIR /app
COPY --from=build-stage /src/build/install/telemetry-service/ ./
EXPOSE 8083
USER app
CMD ["bin/telemetry-service"]
