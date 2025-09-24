# Multi-stage Dockerfile for eth-block-events
# This Dockerfile builds and runs the application in a single process

# Build stage
FROM eclipse-temurin:17-jdk AS build

# Install Maven
RUN apt-get update && apt-get install -y maven && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy all source files
COPY pom.xml ./
COPY src ./src

# Build the application
RUN mvn clean package -DskipTests -B

# Runtime stage
FROM eclipse-temurin:17-jre-alpine

WORKDIR /app

# Create a non-root user for security
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

# Copy the built JAR from the build stage
COPY --from=build /app/target/eth-block-events-1.0.0-SNAPSHOT.jar app.jar

# Change ownership to the non-root user
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose port if the application has web endpoints (optional)
# EXPOSE 8080

# Health check (optional - can be customized based on application endpoints)
# HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
#   CMD wget --no-verbose --tries=1 --spider http://localhost:8080/actuator/health || exit 1

# Run the application
ENTRYPOINT ["java", "-jar", "app.jar"]

# Default arguments (can be overridden)
CMD []