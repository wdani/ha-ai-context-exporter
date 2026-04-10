# HA AI Context Exporter (Add-on scaffold)

This folder contains a minimal Home Assistant add-on scaffold for **HA AI Context Exporter**.

## Current scope

- Small Python backend with a health endpoint (`/health`)
- Minimal static web UI
- Prepared for Home Assistant ingress setup
- No Home Assistant API integration yet
- No export functionality yet

## File overview

- `config.yaml`: Add-on metadata and ingress configuration
- `Dockerfile`: Minimal Python container image
- `run.sh`: Container start script
- `rootfs/app/main.py`: Tiny HTTP server
- `rootfs/app/web/*`: Minimal frontend page and CSS
