# =============================================================================
# UNIFIED DONKEY BETZ PLATFORM - REACT NATIVE/EXPO MOBILE DOCKERFILE
# Multi-stage build for Expo development and web deployment
# =============================================================================

# =============================================================================
# STAGE 1: Base Node Image
# =============================================================================
FROM node:18-alpine as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache \
    git \
    python3 \
    make \
    g++ \
    curl

# Install global dependencies
RUN npm install -g expo-cli @expo/cli eas-cli

# =============================================================================
# STAGE 2: Development Environment
# =============================================================================
FROM base as development

# Copy package files
COPY package*.json ./
COPY app.json ./
COPY expo.json* ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S reactnative -u 1001 && \
    chown -R reactnative:nodejs /app
USER reactnative

# Expose Expo development ports
EXPOSE 8081 19000 19001 19002 19006

# Health check for development server
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8081 || exit 1

# Development command
CMD ["npx", "expo", "start", "--web", "--host", "0.0.0.0", "--port", "8081"]

# =============================================================================
# STAGE 3: Web Build for Production
# =============================================================================
FROM base as web-build

# Copy package files
COPY package*.json ./
COPY app.json ./
COPY expo.json* ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build for web
RUN npx expo export:web

# =============================================================================
# STAGE 4: Web Production with Nginx
# =============================================================================
FROM nginx:alpine as web-production

# Install curl for health checks
RUN apk add --no-cache curl

# Copy nginx configuration
COPY nginx-mobile.conf /etc/nginx/nginx.conf

# Copy built web assets
COPY --from=web-build /app/web-build /usr/share/nginx/html

# Copy mobile-specific entrypoint
COPY mobile-entrypoint.sh /mobile-entrypoint.sh
RUN chmod +x /mobile-entrypoint.sh

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost || exit 1

# Use mobile entrypoint
ENTRYPOINT ["/mobile-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]

# =============================================================================
# STAGE 5: Expo Development Server
# =============================================================================
FROM base as expo-dev

# Copy package files
COPY package*.json ./
COPY app.json ./
COPY expo.json* ./

# Install dependencies including dev dependencies
RUN npm install

# Copy source code
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S expo -u 1001 && \
    chown -R expo:nodejs /app
USER expo

# Expose all Expo ports
EXPOSE 8081 19000 19001 19002 19006

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:19002 || exit 1

# Start Expo development server
CMD ["npx", "expo", "start", "--tunnel", "--host", "0.0.0.0"]

# =============================================================================
# STAGE 6: Standalone Build Environment
# =============================================================================
FROM base as standalone-build

# Install EAS build dependencies
RUN apk add --no-cache \
    openjdk11-jre-headless \
    android-tools

# Set environment variables for Android build
ENV ANDROID_HOME=/opt/android-sdk
ENV PATH="$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools"

# Copy package files
COPY package*.json ./
COPY app.json ./
COPY expo.json* ./
COPY eas.json* ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S builder -u 1001 && \
    chown -R builder:nodejs /app
USER builder

# Build command (to be used with EAS)
CMD ["npx", "eas", "build", "--platform", "all", "--non-interactive"]