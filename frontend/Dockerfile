# ═══════════════════════════════════════════════════════════════════
# Apex Logistics AI — Frontend / Web Proxy Dockerfile
# Production Alpine Nginx Reverse Proxy & Static Asset Server
# Version: 6.0.0
# ═══════════════════════════════════════════════════════════════════

FROM nginx:1.27-alpine

LABEL maintainer="Apex Logistics AI Team"
LABEL version="6.0.0"
LABEL description="Apex Logistics AI — Web Control Tower Frontend & Nginx Reverse Proxy"

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy frontend static files into Nginx public directory
COPY frontend/ /usr/share/nginx/html/

# Expose HTTP port
EXPOSE 80

# Healthcheck for Nginx
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/pages/login.html || exit 1

CMD ["nginx", "-g", "daemon off;"]
