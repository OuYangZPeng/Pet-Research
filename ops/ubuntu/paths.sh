#!/usr/bin/env bash
# Shared path resolution for Shadowmeta Ubuntu scripts.
#
# Canonical layout (flat repo root):
#   /srv/shadowmeta/research-site/.git
#   /srv/shadowmeta/research-site/{web,scraper,ops}
#   /var/www/shadowmeta

SITE_NAME="${SITE_NAME:-shadowmeta}"
APP_ROOT="/srv/${SITE_NAME}"
WEB_ROOT="/var/www/${SITE_NAME}"

# Preferred clone path.
GIT_ROOT="${APP_ROOT}/research-site"

# Back-compat: older installs that used /srv/shadowmeta/repo
if [[ ! -d "${GIT_ROOT}/.git" && -d "${APP_ROOT}/repo/.git" ]]; then
  GIT_ROOT="${APP_ROOT}/repo"
fi

# Flat layout (canonical): web/ and scraper/ live at the git root.
if [[ -d "${GIT_ROOT}/web" && -d "${GIT_ROOT}/scraper" ]]; then
  PROJECT_DIR="${GIT_ROOT}"
# Back-compat: monorepo with an inner research-site/ folder.
elif [[ -d "${GIT_ROOT}/research-site/web" && -d "${GIT_ROOT}/research-site/scraper" ]]; then
  PROJECT_DIR="${GIT_ROOT}/research-site"
else
  PROJECT_DIR="${GIT_ROOT}"
fi
