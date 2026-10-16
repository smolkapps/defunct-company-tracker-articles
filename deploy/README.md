# Deploying defunctcompanies.com

Target setup: static site built by `npm run build` -> `dist/`, served by nginx
on Michael's existing Hetzner server (nginx 1.24, Ubuntu; the same box that
serves `defunct-company-tracker-articles.apps.smolkin.org`), with Cloudflare's
free proxy/CDN in front. DNS lives in Cloudflare; the registrar is Spaceship.

Files in this folder:

| File | Goes to (on the server) | Purpose |
|---|---|---|
| `nginx/defunctcompanies.com.conf` | `/etc/nginx/sites-available/defunctcompanies.com` (+ symlink in `sites-enabled/`) | apex site, www->apex 301, http->https 301, gzip, cache headers, 404 page |
| `nginx/defunctcompanies-tls.conf` | `/etc/nginx/snippets/defunctcompanies-tls.conf` | certificate paths (Cloudflare Origin CA **or** Let's Encrypt) |
| `nginx/defunctcompanies-headers.conf` | `/etc/nginx/snippets/defunctcompanies-headers.conf` | security headers + HSTS |
| `nginx/cloudflare-realip.conf` | `/etc/nginx/conf.d/cloudflare-realip.conf` (optional) | log real visitor IPs instead of Cloudflare's |
| `nginx/old-subdomain-redirect.conf` | edit the existing apps.smolkin.org server block | 301 old URLs -> new domain, path-preserving |
| `deploy.sh` | run locally (Michael's Mac) | build, sanity-check, rsync `dist/` to a new release dir, atomically switch `current` |
| `update-cloudflare-ips.sh` | run on the server occasionally | refresh `cloudflare-realip.conf` |

Placeholders used below: `SERVER_IP` (the Hetzner server's public IPv4, and
`SERVER_IPV6` if it has one), `deploy@SERVER_IP` (an SSH login that can write
to `/var/www/defunctcompanies.com`).

---

## 1. Point the domain at Cloudflare (Spaceship + Cloudflare)

1. **Cloudflare:** dash.cloudflare.com -> *Add a domain* -> `defunctcompanies.com`
   -> Free plan. Cloudflare scans existing records; **delete** any Spaceship
   parking/forwarding records it imports (A/CNAME to Spaceship parking, URL
   forwards).
2. Cloudflare shows two nameservers (e.g. `xxx.ns.cloudflare.com`,
   `yyy.ns.cloudflare.com`).
3. **Spaceship:** *Launchpad -> Domain Manager -> defunctcompanies.com ->
   Nameservers -> Custom nameservers* -> enter the two Cloudflare nameservers ->
   save. Turn off any Spaceship "parking"/"forwarding" for the domain. Leave
   DNSSEC **off** at Spaceship until Cloudflare is active (see step 1.6).
4. Wait for Cloudflare to email "defunctcompanies.com is now active" (minutes
   to a few hours). Check: `dig NS defunctcompanies.com +short`.
5. **DNS records** (Cloudflare -> DNS -> Records):

   | Type | Name | Content | Proxy status |
   |---|---|---|---|
   | A | `@` | `SERVER_IP` | **Proxied** (orange cloud) |
   | AAAA | `@` | `SERVER_IPV6` (only if the server has IPv6 and nginx listens on it) | Proxied |
   | CNAME | `www` | `defunctcompanies.com` | **Proxied** |

   If no email is sent from this domain, also add anti-spoofing records:
   TXT `@` = `v=spf1 -all`, TXT `_dmarc` = `v=DMARC1; p=reject;`.
6. (Optional, after the zone is active) Cloudflare -> DNS -> Settings ->
   *Enable DNSSEC*, then copy the DS record into Spaceship's DNSSEC settings.

## 2. Cloudflare SSL/TLS and caching settings

* **SSL/TLS -> Overview -> encryption mode: `Full (strict)`.** (Not "Flexible":
  that causes redirect loops with the http->https redirect in the nginx config.)
* SSL/TLS -> Edge Certificates: **Always Use HTTPS = On**, Minimum TLS = 1.2,
  Automatic HTTPS Rewrites = On. Leave Cloudflare HSTS off until the site has
  run cleanly for a week or two.
* Caching: defaults are fine. Cloudflare caches `/assets/*` (images, CSS) by
  extension; HTML is not cached at the edge by default, and nginx sends
  `max-age=300` for HTML so updates appear within minutes. After a deploy you
  can force-refresh with *Caching -> Configuration -> Purge Everything*.
* Speed: leave Rocket Loader **off** (the site has no JS to optimise; it can
  only break things).

## 3. Origin certificate on the server (pick ONE)

### Option A (recommended): Cloudflare Origin CA certificate
Free, 15-year, no renewals; trusted only by Cloudflare, which is fine because
the site is always proxied.

1. Cloudflare -> SSL/TLS -> Origin Server -> *Create Certificate* -> "Generate
   private key and CSR with Cloudflare", RSA 2048, hostnames
   `defunctcompanies.com, *.defunctcompanies.com`, validity 15 years.
2. On the server:
   ```bash
   sudo mkdir -p /etc/ssl/cloudflare && sudo chmod 700 /etc/ssl/cloudflare
   sudo nano /etc/ssl/cloudflare/defunctcompanies.com.pem   # paste "Origin Certificate"
   sudo nano /etc/ssl/cloudflare/defunctcompanies.com.key   # paste "Private Key"
   sudo chmod 600 /etc/ssl/cloudflare/defunctcompanies.com.key
   ```
3. `defunctcompanies-tls.conf` already points at these paths (Option A lines).

### Option B: Let's Encrypt via certbot
Works whether or not the proxy is on. Two ways to get the first certificate:

* **HTTP-01 (webroot):** before turning the orange cloud on (set the A/CNAME
  records to *DNS only* temporarily) or with "Always Use HTTPS" off:
  ```bash
  sudo mkdir -p /var/www/letsencrypt
  sudo certbot certonly --webroot -w /var/www/letsencrypt \
       -d defunctcompanies.com -d www.defunctcompanies.com
  ```
  (The port-80 server block already serves `/.well-known/acme-challenge/` from
  `/var/www/letsencrypt`. For the very first run, temporarily comment out the
  443 server blocks or use Option A first, because nginx will not start while
  the Let's Encrypt files don't exist yet.)
* **DNS-01 (works fully proxied, recommended for Option B):**
  ```bash
  sudo apt install python3-certbot-dns-cloudflare
  # Cloudflare -> My Profile -> API Tokens -> "Edit zone DNS" template, zone = defunctcompanies.com
  echo "dns_cloudflare_api_token = <TOKEN>" | sudo tee /root/.cloudflare.ini && sudo chmod 600 /root/.cloudflare.ini
  sudo certbot certonly --dns-cloudflare --dns-cloudflare-credentials /root/.cloudflare.ini \
       -d defunctcompanies.com -d www.defunctcompanies.com
  ```
Then in `defunctcompanies-tls.conf` comment the Option A pair and uncomment
the Option B pair. Renewals run automatically via the certbot systemd timer;
add `--deploy-hook "systemctl reload nginx"` (or a file in
`/etc/letsencrypt/renewal-hooks/deploy/`) so nginx picks them up.

## 4. Install the nginx config on the server

```bash
# from the repo root on the Mac
scp deploy/nginx/defunctcompanies.com.conf deploy/nginx/defunctcompanies-tls.conf \
    deploy/nginx/defunctcompanies-headers.conf deploy/nginx/cloudflare-realip.conf deploy@SERVER_IP:/tmp/

# on the server
sudo mkdir -p /var/www/defunctcompanies.com/releases /var/www/letsencrypt
sudo chown -R deploy:deploy /var/www/defunctcompanies.com      # the user deploy.sh logs in as
sudo install -m 644 /tmp/defunctcompanies.com.conf      /etc/nginx/sites-available/defunctcompanies.com
sudo install -m 644 /tmp/defunctcompanies-tls.conf      /etc/nginx/snippets/defunctcompanies-tls.conf
sudo install -m 644 /tmp/defunctcompanies-headers.conf  /etc/nginx/snippets/defunctcompanies-headers.conf
sudo install -m 644 /tmp/cloudflare-realip.conf         /etc/nginx/conf.d/cloudflare-realip.conf   # optional
sudo ln -s /etc/nginx/sites-available/defunctcompanies.com /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

Notes:
* The config uses `listen 443 ssl http2;`, the correct syntax for nginx 1.24.
  (On nginx >= 1.25.1 it still works but logs a deprecation warning.)
* If `nginx -t` says *could not build server_names_hash*, add
  `server_names_hash_bucket_size 128;` to the `http {}` block of
  `/etc/nginx/nginx.conf` (Ubuntu ships it commented out).
* The config was syntax-checked and smoke-tested locally with nginx 1.26
  (http->https, www->apex and old-subdomain 301s, gzip, cache headers, custom
  404, dotfile blocking).
* Optional hardening: only allow ports 80/443 from Cloudflare's IP ranges
  (ufw/Hetzner Cloud Firewall) so nobody bypasses the CDN.

## 5. Build and deploy (from Michael's Mac)

One-time on the Mac: `brew install rsync` (macOS's built-in openrsync lacks
flags the script uses), Python 3.10+, Node/npm, and SSH access to the server.

```bash
cd defunct-company-tracker-articles
python3 -m venv .venv && .venv/bin/pip install -e ".[test]"
.venv/bin/pytest                                   # 135 tests should pass
DEPLOY_HOST=deploy@SERVER_IP DCT_PYTHON=.venv/bin/python DRY_RUN=1 ./deploy/deploy.sh   # preview
DEPLOY_HOST=deploy@SERVER_IP DCT_PYTHON=.venv/bin/python ./deploy/deploy.sh             # real deploy
```

`deploy.sh` builds with `GT_SITE=https://defunctcompanies.com`, refuses to
deploy if the canonical/sitemap point at another domain, rsyncs into
`/var/www/defunctcompanies.com/releases/<timestamp>/`, flips the `current`
symlink atomically and keeps the last 5 releases. Rollback = point `current`
at an older release (the script prints the command).

Verify:
```bash
curl -sI https://defunctcompanies.com/ | head -5                 # 200, cf-ray header present
curl -sI https://www.defunctcompanies.com/x | grep -i location   # 301 -> https://defunctcompanies.com/x
curl -sI http://defunctcompanies.com/ | grep -i location         # 301 -> https://
curl -s  https://defunctcompanies.com/robots.txt                 # Sitemap: https://defunctcompanies.com/sitemap.xml
curl -s  https://defunctcompanies.com/sitemap.xml | grep -c '<url>'   # 91 at launch
```
Then paste a company URL into https://www.opengraph.xyz/ to check the social card (`/assets/og.png`, 1200x630).

## 6. Redirect the old subdomain (after the new site is verified)

Edit the existing server block for
`defunct-company-tracker-articles.apps.smolkin.org` as shown in
`nginx/old-subdomain-redirect.conf`: keep its `listen`/`ssl_certificate`
lines, replace its `root`/`location` content with the `return 301` lines.
Then `sudo nginx -t && sudo systemctl reload nginx` and check:
```bash
curl -sI https://defunct-company-tracker-articles.apps.smolkin.org/companies/deux.html | grep -i location
# -> https://defunctcompanies.com/companies/deux.html
```
Keep this redirect (and that subdomain's DNS/cert) in place for at least a
year.

## 7. Google Search Console

1. https://search.google.com/search-console -> *Add property* -> **Domain**
   property -> `defunctcompanies.com`.
2. Google shows a TXT record (`google-site-verification=...`). Add it in
   Cloudflare -> DNS -> Records: TXT, name `@`, content = that value
   (Cloudflare also offers a one-click "Verify via Cloudflare" in the GSC flow).
   Click *Verify*.
3. *Sitemaps* -> submit `https://defunctcompanies.com/sitemap.xml`.
4. *URL Inspection* -> inspect `https://defunctcompanies.com/` and
   `https://defunctcompanies.com/collections/shark-tank.html` -> *Request
   indexing*.
5. If the old subdomain was ever verified in Search Console, use *Settings ->
   Change of address* on that old property once the 301s are live.
6. Re-check *Pages* (indexing) and *Performance* weekly for the first month.

## 8. Bing Webmaster Tools (also feeds DuckDuckGo/Yahoo/ChatGPT search)

1. https://www.bing.com/webmasters -> sign in -> **Import from Google Search
   Console** (fastest: imports the verified site and sitemap), or *Add site
   manually* and verify with the CNAME/TXT record Bing gives you (add it in
   Cloudflare DNS).
2. *Sitemaps* -> submit `https://defunctcompanies.com/sitemap.xml`.
3. Optional: *IndexNow* (Bing settings, or Cloudflare -> Caching ->
   Configuration -> Crawler Hints = On) so new pages are picked up faster.

## 9. After launch

* Raise HSTS in `defunctcompanies-headers.conf` to `max-age=31536000` once
  everything has been stable for a couple of weeks.
* Optional: Cloudflare Web Analytics (free, no cookie banner) via
  Cloudflare -> Analytics & Logs -> Web Analytics.
* Each new reviewed research batch: drop the `research_batch_*.json` file into
  `src/dct/data/`, run tests, `./deploy/deploy.sh`. No fixture hand-sync is
  needed any more (see `dct publish` in the main README).
