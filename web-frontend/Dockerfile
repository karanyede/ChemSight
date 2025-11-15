# Web frontend Dockerfile: build + serve with nginx
FROM node:20-alpine as build
WORKDIR /app
COPY web-frontend/package*.json ./
COPY web-frontend/tsconfig*.json ./
COPY web-frontend/ ./
RUN npm ci && npm run build

FROM nginx:1.25-alpine
COPY --from=build /app/dist/ /usr/share/nginx/html/
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
