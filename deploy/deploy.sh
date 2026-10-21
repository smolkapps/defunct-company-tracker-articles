#!/usr/bin/env bash
# Deploy to the actual nginx document root with staging and a full rollback copy.
# The root is updated per-file (--delay-updates), not by a release symlink.
# Usage: DEPLOY_HOST=root@167.233.238.194 DCT_PYTHON=.venv/bin/python3 ./deploy/deploy.sh
set -euo pipefail
cd "$(dirname "$0")/.."

DEPLOY_HOST="${DEPLOY_HOST:?set DEPLOY_HOST}"
DEPLOY_PATH="${DEPLOY_PATH:-/var/www/defunctcompanies.com}"
SSH_PORT="${SSH_PORT:-22}"
SITE_URL="${SITE_URL:-https://defunctcompanies.com}"
BUILD="${BUILD:-1}"
DRY_RUN="${DRY_RUN:-0}"
DCT_PYTHON="${DCT_PYTHON:-python3}"
SSH=(ssh -p "$SSH_PORT" -o BatchMode=yes)
[[ "$DEPLOY_PATH" =~ ^/var/www/[a-zA-Z0-9._-]+$ ]] || { echo 'Invalid document root' >&2; exit 1; }
command -v rsync >/dev/null || { echo 'rsync is required' >&2; exit 1; }
if rsync --version 2>&1 | grep -qi openrsync; then
  echo 'GNU rsync is required (brew install rsync)' >&2
  exit 1
fi
if [[ "$BUILD" == 1 ]]; then
  GT_SITE="$SITE_URL" DCT_PYTHON="$DCT_PYTHON" npm run build
fi
"$DCT_PYTHON" scripts/check_site.py dist
[[ -f dist/index.html && -f dist/sitemap.xml && -f dist/privacy.html ]] || { echo 'Required site files missing' >&2; exit 1; }
[[ -d dist/companies && -n "$(find dist/companies -maxdepth 1 -name '*.html' -print -quit)" ]] || { echo 'No company pages; refusing to replace production' >&2; exit 1; }
grep -Fq "<link rel=\"canonical\" href=\"${SITE_URL}/\"" dist/index.html || { echo 'Wrong canonical origin' >&2; exit 1; }
grep -Fq "<loc>${SITE_URL}/" dist/sitemap.xml || { echo 'Wrong sitemap origin' >&2; exit 1; }

RSYNC_OPTS=(-az --checksum --delete --delay-updates --exclude '._*' --exclude '.DS_Store' --exclude '.git*'
  --chmod=D755,F644 -e "ssh -p ${SSH_PORT} -o BatchMode=yes")
if [[ "$DRY_RUN" == 1 ]]; then
  rsync "${RSYNC_OPTS[@]}" --dry-run --itemize-changes dist/ "$DEPLOY_HOST:$DEPLOY_PATH/"
  exit 0
fi
stage="$("${SSH[@]}" "$DEPLOY_HOST" "mktemp -d '${DEPLOY_PATH}.stage-XXXXXXXX'")"
[[ "$stage" == "${DEPLOY_PATH}.stage-"* && "$stage" =~ ^/var/www/[a-zA-Z0-9._-]+$ ]] || { echo 'Invalid staging path' >&2; exit 1; }
stamp="$(date -u +%Y%m%dT%H%M%SZ)-${stage##*.stage-}"
cleanup() { "${SSH[@]}" "$DEPLOY_HOST" "rm -rf -- '$stage'" || true; }
trap cleanup EXIT
rsync "${RSYNC_OPTS[@]}" dist/ "$DEPLOY_HOST:$stage/"
"${SSH[@]}" "$DEPLOY_HOST" bash -s -- "$DEPLOY_PATH" "$stage" "$stamp" <<'REMOTE'
set -euo pipefail
base="$1"; stage="$2"; stamp="$3"
[[ -d "$base" && ! -L "$base" && -f "$base/index.html" ]] || { echo 'Expected existing direct document root' >&2; exit 1; }
exec 9>"${base}.deploy.lock"
flock -n 9 || { echo 'Another deployment owns this site' >&2; exit 1; }
backup="${base}.backups/${stamp}"
mkdir -p "$backup"
cp -a "$base/." "$backup/"
trap 'rsync -a --delete "$backup/" "$base/"; echo "Deployment failed; restored $backup" >&2' ERR
rsync -a --delete --delay-updates "$stage/" "$base/"
test -f "$base/privacy.html"
trap - ERR
echo "Deployed to $base; full backup $backup"
echo "Rollback: rsync -a --delete '$backup/' '$base/'"
REMOTE
