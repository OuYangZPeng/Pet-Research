#!/usr/bin/env bash
set -euo pipefail

# Bootstrap an Ubuntu server for the Shadowmeta pet-research site.
#
# Usage:
#   DOMAIN=shadowmeta.com REPO_URL=git@github.com:you/research-site.git \
#   bash ops/ubuntu/bootstrap_shadowmeta.sh
#
# Optional:
#   SITE_NAME=shadowmeta
#   BRANCH=main
#   ENABLE_HTTPS=1
#   WWW_DOMAIN=www.shadowmeta.com

SITE_NAME="${SITE_NAME:-shadowmeta}"
DOMAIN="${DOMAIN:-shadowmeta.com}"
WWW_DOMAIN="${WWW_DOMAIN:-www.${DOMAIN}}"
REPO_URL="${REPO_URL:-}"
BRANCH="${BRANCH:-main}"
ENABLE_HTTPS="${ENABLE_HTTPS:-0}"

APP_ROOT="/srv/${SITE_NAME}"
REPO_DIR="${APP_ROOT}/research-site"
WEB_ROOT="/var/www/${SITE_NAME}"
CURRENT_USER="${SUDO_USER:-$USER}"

if [[ -z "${REPO_URL}" ]]; then
  echo "REPO_URL is required."
  exit 1
fi

if ! command -v apt-get >/dev/null 2>&1; then
  echo "This bootstrap script targets Ubuntu/Debian systems with apt-get."
  exit 1
fi

echo "[bootstrap] installing system packages..."
sudo apt-get update
sudo apt-get install -y \
  ca-certificates \
  certbot \
  curl \
  git \
  nginx \
  python3 \
  python3-pip \
  python3-venv \
  python3-certbot-nginx \
  rsync

if ! command -v node >/dev/null 2>&1; then
  echo "[bootstrap] installing Node.js 20..."
  curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
  sudo apt-get install -y nodejs
fi

echo "[bootstrap] creating application directories..."
sudo mkdir -p "${APP_ROOT}" "${WEB_ROOT}"
sudo chown -R "${CURRENT_USER}:${CURRENT_USER}" "${APP_ROOT}" "${WEB_ROOT}"

if [[ ! -d "${REPO_DIR}/.git" ]]; then
  echo "[bootstrap] cloning repository..."
  git clone --branch "${BRANCH}" "${REPO_URL}" "${REPO_DIR}"
else
  echo "[bootstrap] repository already exists; pulling latest..."
  git -C "${REPO_DIR}" checkout "${BRANCH}"
  git -C "${REPO_DIR}" pull --ff-only
fi

echo "[bootstrap] preparing scraper virtualenv..."
cd "${REPO_DIR}/scraper"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .
playwright install chromium --with-deps
cp -n .env.example .env

echo "[bootstrap] installing web dependencies..."
cd "${REPO_DIR}/web"
npm ci
npm run build
rsync -a --delete dist/ "${WEB_ROOT}/"

echo "[bootstrap] installing nginx config..."
TEMPLATE="${REPO_DIR}/ops/ubuntu/shadowmeta.nginx.conf"
TMP_CONF="$(mktemp)"
sed \
  -e "s|__DOMAIN__|${DOMAIN}|g" \
  -e "s|__WWW_DOMAIN__|${WWW_DOMAIN}|g" \
  -e "s|__WEB_ROOT__|${WEB_ROOT}|g" \
  "${TEMPLATE}" > "${TMP_CONF}"
sudo mv "${TMP_CONF}" "/etc/nginx/sites-available/${SITE_NAME}"
sudo ln -sf "/etc/nginx/sites-available/${SITE_NAME}" "/etc/nginx/sites-enabled/${SITE_NAME}"
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx

if [[ "${ENABLE_HTTPS}" == "1" ]]; then
  echo "[bootstrap] requesting Let's Encrypt certificate..."
  sudo certbot --nginx -d "${DOMAIN}" -d "${WWW_DOMAIN}"
fi

cat <<EOF

[bootstrap] done.

Next steps:
1. Edit scraper env:
   nano "${REPO_DIR}/scraper/.env"
2. Run a manual refresh once:
   bash "${REPO_DIR}/ops/ubuntu/refresh_shadowmeta.sh"
3. Install cron:
   crontab -e
   # then copy from:
   cat "${REPO_DIR}/ops/ubuntu/shadowmeta.cron.example"

EOF
