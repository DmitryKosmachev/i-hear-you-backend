FROM nginx:1.29.1
COPY nginx.conf /etc/nginx/templates/default.conf.template
COPY --from=vpetruin/i-hear-you-admin-panel:latest /app/dist/ /usr/share/nginx/html/