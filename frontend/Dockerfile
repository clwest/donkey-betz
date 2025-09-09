# =============================================================================
# UNIFIED DONKEY BETZ PLATFORM - REACT FRONTEND DOCKERFILE
# Multi-stage build for optimized production deployment
# =============================================================================

# =============================================================================
# STAGE 1: Development Build
# =============================================================================
FROM node:18-alpine as development

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache git

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001 && \
    chown -R nextjs:nodejs /app
USER nextjs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Development command
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]

# =============================================================================
# STAGE 2: Production Build
# =============================================================================
FROM node:18-alpine as build

# Set working directory
WORKDIR /app

# Install system dependencies for build
RUN apk add --no-cache git python3 make g++

# Copy package files
COPY package*.json ./

# Install dependencies with production optimizations
RUN npm ci --only=production && npm cache clean --force

# Copy source code
COPY . .

# Build for production
RUN npm run build

# =============================================================================
# STAGE 3: Production Runtime with Nginx
# =============================================================================
FROM nginx:alpine as production

# Install curl for health checks
RUN apk add --no-cache curl

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy environment configuration script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Create non-root user for nginx
RUN adduser -D -s /bin/sh nginxuser

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost || exit 1

# Use entrypoint script for environment variable injection
ENTRYPOINT ["/docker-entrypoint.sh"]

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

# =============================================================================
# STAGE 4: Development with Hot Reload
# =============================================================================
FROM node:18-alpine as development-hot

# Set working directory
WORKDIR /app

# Install dependencies
RUN apk add --no-cache git

# Copy package files
COPY package*.json ./

# Install all dependencies including dev dependencies
RUN npm install

# Copy source code
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001 && \
    chown -R nextjs:nodejs /app
USER nextjs

# Expose port and HMR port
EXPOSE 3000 24678

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Development command with hot reload
CMD ["npm", "run", "dev"]