# WHAT DOES THIS FILE DO: Multi-stage production build — Vite builds static assets, nginx serves them.

# ================== BUILD STAGE ==================
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build
# ================== BUILD STAGE ==================


# ================== SERVE STAGE ==================
FROM nginx:alpine

# Vite's build output directory is dist/, not build/ (that's Create React App's convention —
# this project uses Vite, see frontend's own setup for why).
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
# ================== SERVE STAGE ==================
