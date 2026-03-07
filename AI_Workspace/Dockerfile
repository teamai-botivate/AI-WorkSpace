# ============================================================
# Stage 1: Build Frontend
# ============================================================
FROM node:20-alpine AS frontend-build

WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ============================================================
# Stage 2: Build Backend + Serve with Nginx
# ============================================================
FROM python:3.11-slim AS production

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/
COPY workspace.config.json ./workspace.config.json

# Copy built frontend
COPY --from=frontend-build /frontend/dist /app/frontend/dist

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Create data directories
RUN mkdir -p /app/data/chroma /app/data/uploads /app/data/agents/hr_support /app/data/agents/resume_screening

# Expose port
EXPOSE 80

# Start script: run backend + nginx
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
CMD ["/docker-entrypoint.sh"]
