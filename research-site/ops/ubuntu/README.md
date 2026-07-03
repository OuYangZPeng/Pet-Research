# Ubuntu Deployment

This folder contains a ready-to-run deployment setup for the pet-only
`shadowmeta` research site on Ubuntu.

## Files

- `bootstrap_shadowmeta.sh`: first-time server setup
- `deploy_shadowmeta.sh`: pull code, build frontend, publish to nginx
- `refresh_shadowmeta.sh`: pull code, run scraper jobs, build frontend, publish
- `shadowmeta.nginx.conf`: nginx template used by bootstrap
- `shadowmeta.cron.example`: weekly cron example

## Recommended server flow

1. Push the latest code from your Mac to your git remote.
2. On the Ubuntu server, run:

```bash
DOMAIN=shadowmeta.com REPO_URL=git@github.com:YOUR_ORG/YOUR_REPO.git \
bash ops/ubuntu/bootstrap_shadowmeta.sh
```

3. Edit scraper credentials:

```bash
nano /srv/shadowmeta/research-site/scraper/.env
```

At minimum:

- `RAINFOREST_API_KEY`
- `YOUTUBE_API_KEY`
- `CURSOR_API_KEY` if you want fully automatic review insights
- `REDDIT_CLIENT_ID`
- `REDDIT_CLIENT_SECRET`

4. Run a manual full refresh once:

```bash
bash /srv/shadowmeta/research-site/ops/ubuntu/refresh_shadowmeta.sh
```

5. Install cron:

```bash
crontab -e
```

Then copy the line from `shadowmeta.cron.example`.

## Notes

- The scripts assume nginx web root is `/var/www/shadowmeta`.
- The scripts assume repo checkout is `/srv/shadowmeta/research-site`.
- If your actual domain is not `shadowmeta.com`, override `DOMAIN=...` during bootstrap.
- If the server is in mainland China, YouTube / Reddit / Google Trends access may be unstable.
