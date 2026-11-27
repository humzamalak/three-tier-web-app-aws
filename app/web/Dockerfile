# syntax=docker/dockerfile:1
# Images come from Amazon ECR Public to avoid Docker Hub pull limits.
# nginx-unprivileged runs as a non-root user and listens on 8080.
FROM public.ecr.aws/nginx/nginx-unprivileged:1.30-alpine
# Pick up Alpine security fixes released after the base image was built.
USER root
RUN apk upgrade --no-cache
USER 101
ENV API_UPSTREAM=http://api:8000
COPY default.conf.template /etc/nginx/templates/default.conf.template
COPY public/ /usr/share/nginx/html/
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD wget -qO- http://127.0.0.1:8080/healthz || exit 1
