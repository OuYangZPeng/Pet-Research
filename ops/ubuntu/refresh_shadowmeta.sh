#!/usr/bin/env bash
set -euo pipefail

# Full weekly refresh for the Shadowmeta pet-research site:
# 1. pull latest code
# 2. run scraper jobs
# 3. build the frontend
# 4. publish dist/ to nginx web root
#
# Usage:
#   bash /srv/shadowmeta/research-site/ops/ubuntu/refresh_shadowmeta.sh
#
# Optional:
#   SITE_NAME=shadowmeta
#   BRANCH=main
#   VIDEO_LOOKBACK=1,2,3,all

SITE_NAME="${SITE_NAME:-shadowmeta}"
BRANCH="${BRANCH:-main}"
VIDEO_LOOKBACK="${VIDEO_LOOKBACK:-1,2,3,all}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/paths.sh"

if [[ ! -d "${GIT_ROOT}/.git" ]]; then
  echo "[refresh] git root not found: ${GIT_ROOT}"
  exit 1
fi

if [[ ! -d "${PROJECT_DIR}/scraper" || ! -d "${PROJECT_DIR}/web" ]]; then
  echo "[refresh] project dirs not found under: ${PROJECT_DIR}"
  exit 1
fi

echo "[refresh] project dir: ${PROJECT_DIR}"

echo "[refresh] updating repository..."
cd "${GIT_ROOT}"
git checkout "${BRANCH}"
git pull --ff-only

echo "[refresh] preparing scraper env..."
cd "${PROJECT_DIR}/scraper"
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

echo "[refresh] running core dataset refresh..."
python run_all.py

echo "[refresh] regenerating review insights..."
python refresh_reviews.py --force

if [[ -n "${YOUTUBE_API_KEY:-}" ]]; then
  echo "[refresh] refreshing per-SKU YouTube videos..."
  python refresh_videos.py --lookback "${VIDEO_LOOKBACK}"
else
  echo "[refresh] YOUTUBE_API_KEY missing; skipping refresh_videos.py"
fi

echo "[refresh] building frontend..."
cd "${PROJECT_DIR}/web"
npm ci
npm run build

echo "[refresh] publishing to nginx web root..."
rsync -a --delete dist/ "${WEB_ROOT}/"
sudo nginx -t
sudo systemctl reload nginx

echo "[refresh] done."
