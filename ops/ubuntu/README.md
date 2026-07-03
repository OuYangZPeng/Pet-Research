# Ubuntu Deployment

Canonical server layout:

```text
/srv/shadowmeta/research-site/     # git clone (flat repo root)
  web/
  scraper/
  ops/ubuntu/
/var/www/shadowmeta/               # nginx web root
```

## Files

- `paths.sh`: shared path resolution
- `bootstrap_shadowmeta.sh`: first-time server setup
- `deploy_shadowmeta.sh`: pull code, build frontend, publish to nginx
- `refresh_shadowmeta.sh`: pull code, run scraper, build, publish
- `shadowmeta.nginx.conf`: nginx template
- `shadowmeta.cron.example`: weekly cron example

## Fresh install

On Ubuntu:

```bash
# wipe any previous broken install
sudo rm -rf /srv/shadowmeta /var/www/shadowmeta

sudo mkdir -p /srv/shadowmeta
sudo chown -R "$USER:$USER" /srv/shadowmeta

# clone bootstrap scripts temporarily, or clone the full repo first
git clone git@github.com:OuYangZPeng/Pet-Research.git /tmp/pet-research

DOMAIN=shadowmeta.com \
REPO_URL=git@github.com:OuYangZPeng/Pet-Research.git \
ENABLE_HTTPS=1 \
bash /tmp/pet-research/ops/ubuntu/bootstrap_shadowmeta.sh
```

Then:

```bash
nano /srv/shadowmeta/research-site/scraper/.env
bash /srv/shadowmeta/research-site/ops/ubuntu/refresh_shadowmeta.sh
crontab -e   # paste from ops/ubuntu/shadowmeta.cron.example
```
