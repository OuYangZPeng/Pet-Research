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

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/paths.sh"

if [[ ! -d "${GIT_ROOT}/.git" ]]; then
  echo "[deploy] git root not found: ${GIT_ROOT}"
  exit 1
fi

if [[ ! -d "${PROJECT_DIR}/web" ]]; then
  echo "[deploy] project web/ not found: ${PROJECT_DIR}/web"
  exit 1
fi

echo "[deploy] project dir: ${PROJECT_DIR}"

echo "[deploy] updating repository..."
cd "${GIT_ROOT}"
git checkout "${BRANCH}"
git pull --ff-only

echo "[deploy] building frontend..."
cd "${PROJECT_DIR}/web"
npm ci
npm run build

echo "[deploy] syncing dist to nginx web root..."
rsync -a --delete dist/ "${WEB_ROOT}/"
sudo nginx -t
sudo systemctl reload nginx

echo "[deploy] done."
