FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package*.json tsconfig.json ./
RUN npm install

# Copy source files
COPY src ./src

# Compile TypeScript -> dist
RUN npx tsc

# Debug: show compiled files
RUN echo "=== DIST CONTENT ===" && ls -R dist && \
    echo "=== SERVER.JS CONTENT ===" && cat dist/server.js

# ---- Runtime ----
FROM node:20-alpine AS runtime
WORKDIR /app

# Copy only necessary files from builder
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
COPY package*.json ./

# Run compiled server
CMD ["node", "dist/server.js"]
