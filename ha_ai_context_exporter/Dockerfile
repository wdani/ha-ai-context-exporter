FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY rootfs/app /app
COPY run.sh /run.sh
RUN chmod +x /run.sh

EXPOSE 8099

ENTRYPOINT ["/run.sh"]
