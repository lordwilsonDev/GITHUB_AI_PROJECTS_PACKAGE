# --- Stage 1: The Builder (High Density) ---
FROM node:20-alpine AS builder
WORKDIR /app

# 🛠️ FIX: Install build tools required for redis-memory-server/gyp
RUN apk add --no-cache python3 make g++

# Copy manifest files
COPY package*.json ./

# Install ALL dependencies (including dev tools)
RUN npm install

# Copy source code
COPY . .

# --- Stage 2: The Runner (High Vitality) ---
FROM node:20-alpine
WORKDIR /app

# 🛠️ FIX: Install build tools here too (for production native modules)
RUN apk add --no-cache python3 make g++

COPY package*.json ./
# Install ONLY production dependencies
RUN npm install --production

# Install Motia CLI globally
RUN npm install -g motia

# Copy source code and config
COPY --from=builder /app ./
COPY motia.config.ts ./

EXPOSE 3000
CMD ["npx", "motia", "start"]
