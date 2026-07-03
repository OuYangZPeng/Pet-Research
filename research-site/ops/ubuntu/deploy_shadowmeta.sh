#!/usr/bin/env bash
set -euo pipefail

# Pull latest code, build the frontend, and publish to nginx web root.
#
# Usage:
#   bash /srv/shadowmeta/research-site/ops/ubuntu/deploy_shadowmeta.sh
#
# Optional:
#   SITE_NAME=shadowmeta
#   BRANCH=main

SITE_NAME="${SITE_NAME:-shadowmeta}"
BRANCH="${BRANCH:-main}"

APP_ROOT="/srv/${SITE_NAME}"
REPO_DIR="${APP_ROOT}/research-site"
WEB_ROOT="/var/www/${SITE_NAME}"

echo "[deploy] updating repository..."
cd "${REPO_DIR}"
git checkout "${BRANCH}"
git pull --ff-only

echo "[deploy] building frontend..."
cd "${REPO_DIR}/web"
npm ci
npm run build

echo "[deploy] syncing dist to nginx web root..."
rsync -a --delete dist/ "${WEB_ROOT}/"
sudo nginx -t
sudo systemctl reload nginx

echo "[deploy] done."
