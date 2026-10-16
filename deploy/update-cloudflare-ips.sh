#!/usr/bin/env bash
# Regenerate cloudflare-realip.conf from Cloudflare's published IP ranges.
# Run on the web server (or locally, then copy):  sudo ./update-cloudflare-ips.sh
set -euo pipefail
OUT="${1:-/etc/nginx/conf.d/cloudflare-realip.conf}"
tmp="$(mktemp)"
{
  echo "# Generated $(date -u +%Y-%m-%dT%H:%M:%SZ) from https://www.cloudflare.com/ips-v4 and /ips-v6"
  for ip in $(curl -fsS https://www.cloudflare.com/ips-v4) $(curl -fsS https://www.cloudflare.com/ips-v6); do
    echo "set_real_ip_from ${ip};"
  done
  echo "real_ip_header CF-Connecting-IP;"
} > "$tmp"
grep -q set_real_ip_from "$tmp" || { echo "no ranges fetched; leaving $OUT unchanged" >&2; exit 1; }
install -m 0644 "$tmp" "$OUT"
rm -f "$tmp"
if command -v nginx >/dev/null; then nginx -t && systemctl reload nginx; fi
echo "updated $OUT"
