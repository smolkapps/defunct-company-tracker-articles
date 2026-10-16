#!/usr/bin/env bash
# Deploy the built static site (dist/) to the web server with rsync.
#
# Atomic, rollback-friendly layout on the server:
#   $DEPLOY_PATH/releases/<UTC timestamp>/   one directory per deploy
#   $DEPLOY_PATH/current -> releases/<ts>    nginx root points here
# Unchanged files are hard-linked from the previous release (--link-dest),
# so each release costs almost no extra disk space.
#
# Usage (from the repo root, on a machine that can SSH to the server):
#   DEPLOY_HOST=deploy@203.0.113.10 ./deploy/deploy.sh
#
# Environment:
#   DEPLOY_HOST   (required) ssh target, e.g. root@1.2.3.4 or an ~/.ssh/config alias
#   DEPLOY_PATH   remote base dir            (default /var/www/defunctcompanies.com)
#   SSH_PORT      ssh port                   (default 22)
#   SITE_URL      expected canonical origin  (default https://defunctcompanies.com)
#   BUILD=1       run `npm run build` first  (default 1; set 0 to deploy dist/ as-is)
#   KEEP=5        releases to keep on the server
#   DRY_RUN=1     show what rsync would do; change nothing on the server
set -euo pipefail

cd "$(dirname "$0")/.."

DEPLOY_HOST="${DEPLOY_HOST:?set DEPLOY_HOST, e.g. DEPLOY_HOST=deploy@your-server}"
DEPLOY_PATH="${DEPLOY_PATH:-/var/www/defunctcompanies.com}"
SSH_PORT="${SSH_PORT:-22}"
SITE_URL="${SITE_URL:-https://defunctcompanies.com}"
BUILD="${BUILD:-1}"
KEEP="${KEEP:-5}"
DRY_RUN="${DRY_RUN:-0}"
SSH=(ssh -p "$SSH_PORT" -o BatchMode=yes)

command -v rsync >/dev/null || { echo "rsync not found (macOS: brew install rsync; Ubuntu: apt install rsync)" >&2; exit 1; }
# macOS 15+ ships "openrsync", which lacks some flags used here (--chmod,
# --itemize-changes). Install GNU rsync with:  brew install rsync
if rsync --version 2>&1 | grep -qi openrsync; then
  echo "openrsync detected; install GNU rsync (brew install rsync) and make sure it is first in PATH" >&2
  exit 1
fi

if [[ "$BUILD" == "1" ]]; then
  GT_SITE="$SITE_URL" npm run build
fi

# --- sanity checks: never ship an empty build or one pointing at the wrong domain
[[ -f dist/index.html && -f dist/sitemap.xml ]] || { echo "dist/ is missing index.html or sitemap.xml" >&2; exit 1; }
grep -q "<link rel=\"canonical\" href=\"${SITE_URL}/\"" dist/index.html \
  || { echo "dist/index.html canonical is not ${SITE_URL}/ -- rebuild with GT_SITE=${SITE_URL}" >&2; exit 1; }
grep -q "<loc>${SITE_URL}/" dist/sitemap.xml \
  || { echo "dist/sitemap.xml does not use ${SITE_URL}" >&2; exit 1; }
n_articles=$(find dist/companies -name '*.html' | wc -l)
(( n_articles > 0 )) || { echo "no company pages in dist/" >&2; exit 1; }
echo "build OK: ${n_articles} company pages, $(grep -c '<url>' dist/sitemap.xml) sitemap URLs"

RELEASE="$(date -u +%Y%m%dT%H%M%SZ)"
REMOTE_REL="${DEPLOY_PATH}/releases/${RELEASE}"
RSYNC_OPTS=(-az --delete --checksum
  --exclude '._*' --exclude '.DS_Store' --exclude '.git*'
  --chmod=D755,F644
  -e "ssh -p ${SSH_PORT} -o BatchMode=yes")

if [[ "$DRY_RUN" == "1" ]]; then
  echo "DRY RUN: rsync -> ${DEPLOY_HOST}:${REMOTE_REL}/"
  rsync "${RSYNC_OPTS[@]}" --dry-run --itemize-changes dist/ "${DEPLOY_HOST}:${DEPLOY_PATH}/current/" || true
  exit 0
fi

"${SSH[@]}" "$DEPLOY_HOST" "mkdir -p '${DEPLOY_PATH}/releases'"
rsync "${RSYNC_OPTS[@]}" --link-dest="${DEPLOY_PATH}/current/" dist/ "${DEPLOY_HOST}:${REMOTE_REL}/"

# switch the symlink atomically, then prune old releases
"${SSH[@]}" "$DEPLOY_HOST" bash -s -- "$DEPLOY_PATH" "$RELEASE" "$KEEP" <<'REMOTE'
set -euo pipefail
base="$1"; rel="$2"; keep="$3"
ln -sfn "releases/$rel" "$base/current.tmp"
mv -T "$base/current.tmp" "$base/current"
cd "$base/releases"
ls -1d */ 2>/dev/null | sed 's#/$##' | sort | head -n -"$keep" | xargs -r rm -rf --
echo "current -> $(readlink "$base/current")"
REMOTE

echo "deployed release ${RELEASE} to ${DEPLOY_HOST}:${DEPLOY_PATH}/current"
echo "rollback: ssh ${DEPLOY_HOST} 'ln -sfn releases/<older-ts> ${DEPLOY_PATH}/current.tmp && mv -T ${DEPLOY_PATH}/current.tmp ${DEPLOY_PATH}/current'"
echo "verify:   curl -sI ${SITE_URL}/ | head -5"
