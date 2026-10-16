"""Static site generator.

Renders the verified status reports into a self-contained static website:

    out/
      index.html            (table of verified companies + collapsed unverified)
      methodology.html       (how statuses are determined / verified)
      companies/<slug>.html  (one article per VERIFIED company)
      status/<status>.html   (hub: verified companies with that status)
      collections/<name>.html (hub: Shark Tank companies vs other companies)
      assets/style.css

Only :pyattr:`StatusReport.publishable` reports get their own article page and
appear in the main index — unverified ones are listed (name + reason) in a
collapsed section so the withholding is transparent but never presented as fact.

Each article embeds JSON-LD so the pages are machine-readable, plus a sitemap is
emitted for the whole site.
"""

from __future__ import annotations

import json
import os
import re
import shutil
from datetime import datetime, timezone
from typing import Any, Iterable

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .models import Status, StatusReport
from .pipeline import PipelineResult

SHARK_TANK_TAG = "shark-tank"

#: human labels for status hub pages (only statuses with >=1 published company
#: get a page)
STATUS_HUB_LABELS: dict[str, tuple[str, str]] = {
    "active": ("Still in business", "Companies verified as still operating."),
    "acquired": ("Acquired companies", "Companies verified as acquired by another business."),
    "merged": ("Merged companies", "Companies verified as merged into another entity."),
    "defunct": ("Defunct companies", "Companies verified as closed, dissolved or no longer operating."),
    "bankrupt": ("Bankrupt companies", "Companies verified as having gone through bankruptcy."),
    "renamed": ("Renamed companies", "Companies verified as now trading under a different name."),
    "canceled": ("Canceled companies", "Companies verified as canceled."),
    "dissolved_recreated": ("Dissolved and recreated", "Companies dissolved and later recreated."),
}

COLLECTIONS: dict[str, tuple[str, str]] = {
    "shark-tank": (
        "Shark Tank companies: where are they now?",
        "Businesses that pitched on ABC's Shark Tank, with their verified current status and sources.",
    ),
    "other-companies": (
        "Other notable companies",
        "Well-known companies outside Shark Tank, tracked with the same source-cited method.",
    ),
}

_PKG_DIR = os.path.dirname(os.path.abspath(__file__))
# templates/static are shipped INSIDE the package so the generator works both
# from a source checkout and from an installed wheel.
DEFAULT_TEMPLATE_DIR = os.path.join(_PKG_DIR, "templates")
DEFAULT_STATIC_DIR = os.path.join(_PKG_DIR, "static")
DEFAULT_UMAMI_SCRIPT_URL = "https://umami.smolkin.org/script.js"


def _jsonld_for(report: StatusReport, site_url: str) -> str:
    """An Organization schema.org node describing the company + status."""
    site_base = site_url.rstrip("/") if site_url else ""
    article_url = (
        f"{site_base}/companies/{report.company.slug}.html" if site_base else None
    )
    node = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": report.company.name,
        "description": report.summary,
        "dissolutionDate": report.as_of
        if report.status in {Status.DEFUNCT, Status.BANKRUPT} and report.as_of
        else None,
        "parentOrganization": {"@type": "Organization", "name": report.successor}
        if report.status == Status.ACQUIRED and report.successor
        else None,
        "url": _absolute_url(report.company.domain),
        "mainEntityOfPage": article_url,
        "alternateName": list(report.company.aliases) or None,
        "subjectOf": [
            {"@type": "WebPage", "url": c.url, "name": c.title}
            for c in report.citations
        ]
        or None,
    }
    node = {k: v for k, v in node.items() if v is not None}
    return _json_for_script(node)


def _breadcrumb_jsonld(
    report: StatusReport,
    site_url: str,
    collection_hub: dict[str, Any] | None = None,
    status_hub: dict[str, Any] | None = None,
    research_only: bool = False,
) -> str:
    """A BreadcrumbList schema.org node for an article page."""
    base = site_url.rstrip("/") if site_url else ""
    items: list[dict[str, Any]] = [
        {
            "@type": "ListItem",
            "position": 1,
            "name": "All companies",
            "item": f"{base}/" if base else "index.html",
        }
    ]
    pos = 2
    if collection_hub:
        items.append(
            {
                "@type": "ListItem",
                "position": pos,
                "name": collection_hub["label"],
                "item": (
                    f"{base}/{collection_hub['path']}"
                    if base
                    else collection_hub["path"]
                ),
            }
        )
        pos += 1
    if not research_only and status_hub:
        items.append(
            {
                "@type": "ListItem",
                "position": pos,
                "name": status_hub["title"],
                "item": (
                    f"{base}/{status_hub['path']}" if base else status_hub["path"]
                ),
            }
        )
        pos += 1
    items.append(
        {
            "@type": "ListItem",
            "position": pos,
            "name": report.company.name,
            "item": (
                f"{base}/companies/{report.company.slug}.html"
                if base
                else f"companies/{report.company.slug}.html"
            ),
        }
    )
    return _json_for_script(
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": items,
        }
    )


def _website_jsonld(
    site_name: str, site_description: str, site_url: str, n_verified: int
) -> str:
    """WebSite schema.org node for the home page."""
    base = site_url.rstrip("/") if site_url else ""
    node: dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": site_name,
        "description": site_description,
    }
    if base:
        node["url"] = f"{base}/"
    node["about"] = {
        "@type": "Dataset",
        "name": f"{site_name} Verified Corporate Status Dataset",
        "description": (
            f"Source-cited operational statuses for {n_verified} verified companies."
        ),
    }
    return _json_for_script(node)


def _webpage_jsonld(
    title: str, description: str, url: str, site_name: str, site_url: str
) -> str:
    """WebPage schema.org node for static informational pages."""
    node: dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": title,
        "description": description,
        "isPartOf": {"@type": "WebSite", "name": site_name},
    }
    if url:
        node["url"] = url
    if site_url:
        node["isPartOf"]["url"] = f"{site_url.rstrip('/')}/"
    return _json_for_script(node)


def _absolute_url(domain: str | None) -> str | None:
    """schema.org ``url`` must be absolute; bare domains get ``https://``."""
    if not domain:
        return None
    d = domain.strip()
    return d if re.match(r"^https?://", d, re.I) else f"https://{d}"


def _json_for_script(obj) -> str:
    """Serialize ``obj`` as JSON safe to embed inside an HTML ``<script>`` tag.

    A company name like ``Evil </script>...`` would otherwise close the
    JSON-LD script element and allow markup/JS injection. Escaping ``<``, ``>``
    and ``&`` to their ``\\uXXXX`` forms keeps the JSON valid while making it
    impossible to break out of the script context — the standard mitigation
    used by Django's ``json_script`` and others.
    """
    raw = json.dumps(obj, ensure_ascii=False, indent=2)
    return raw.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def _episode_keys(detail: dict[str, Any] | None) -> set[tuple[int, int]]:
    """Extract (season, episode) pairs from a research record."""
    if not detail:
        return set()
    keys: set[tuple[int, int]] = set()
    for app in detail.get("episode_appearances") or []:
        season = app.get("season")
        episode = app.get("episode")
        if isinstance(season, int) and isinstance(episode, int):
            keys.add((season, episode))
    return keys


class SiteGenerator:
    def __init__(
        self,
        site_name: str = "Defunct Company Tracker",
        site_description: str = (
            "Is it still in business? Machine-researched, source-cited corporate "
            "statuses — active, acquired, or defunct."
        ),
        site_url: str = "",
        template_dir: str = DEFAULT_TEMPLATE_DIR,
        static_dir: str = DEFAULT_STATIC_DIR,
        umami_website_id: str | None = None,
        umami_script_url: str | None = None,
    ) -> None:
        self.site_name = site_name
        self.site_description = site_description
        self.site_url = site_url.rstrip("/")
        self.template_dir = template_dir
        self.static_dir = static_dir
        if umami_website_id is None:
            umami_website_id = (
                os.environ.get("DCT_UMAMI_WEBSITE_ID")
                or os.environ.get("UMAMI_WEBSITE_ID")
                or ""
            )
        if umami_script_url is None:
            umami_script_url = (
                os.environ.get("DCT_UMAMI_SCRIPT_URL")
                or os.environ.get("UMAMI_SCRIPT_URL")
                or DEFAULT_UMAMI_SCRIPT_URL
            )
        self.umami_website_id = umami_website_id.strip()
        self.umami_script_url = (
            umami_script_url.strip() or DEFAULT_UMAMI_SCRIPT_URL
        )
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def _ctx(self, **extra) -> dict:
        base = {
            "site_name": self.site_name,
            "site_description": self.site_description,
            "site_url": self.site_url,
            "og_image_url": f"{self.site_url}/assets/og.png" if self.site_url else "",
            "has_shark_hub": getattr(self, "_has_shark_hub", False),
            "umami_website_id": self.umami_website_id,
            "umami_script_url": (
                self.umami_script_url if self.umami_website_id else ""
            ),
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        }
        base.update(extra)
        return base

    def build(
        self,
        result: PipelineResult,
        out_dir: str,
        research_records: Iterable[dict[str, Any]] = (),
    ) -> dict[str, int]:
        os.makedirs(out_dir, exist_ok=True)
        companies_dir = os.path.join(out_dir, "companies")
        os.makedirs(companies_dir, exist_ok=True)
        assets_dir = os.path.join(out_dir, "assets")
        os.makedirs(assets_dir, exist_ok=True)

        # copy static assets
        if os.path.isdir(self.static_dir):
            for fn in os.listdir(self.static_dir):
                if fn.startswith("._") or fn == ".DS_Store":
                    continue  # macOS metadata, never publish
                shutil.copy2(
                    os.path.join(self.static_dir, fn), os.path.join(assets_dir, fn)
                )

        published = result.publishable
        unpublished = result.unpublishable
        research_by_name = {
            record["company"]["name"].casefold(): record
            for record in research_records
        }

        def is_shark_tank(r: StatusReport) -> bool:
            return (
                SHARK_TANK_TAG in r.company.tags
                or r.company.name.casefold() in research_by_name
            )

        self._has_shark_hub = any(is_shark_tank(r) for r in published)

        n_companies = len(result.reports)
        root_url = f"{self.site_url}/" if self.site_url else ""
        published_by_slug = {r.company.slug: r for r in published}
        episode_primary = published_by_slug.get("fish-fixe")
        episode_second_tier = [
            published_by_slug[slug]
            for slug in ("hello-prenup", "deux", "hidrent")
            if slug in published_by_slug
        ]

        # Precompute hub metadata and episode groupings so article pages can
        # link to their collection hub, status hub, episode companions, and
        # related companies.
        status_hubs: list[dict[str, Any]] = []
        status_hub_by_val: dict[str, dict[str, Any]] = {}
        members_by_status: dict[str, list[StatusReport]] = {}
        for value, (title, intro) in STATUS_HUB_LABELS.items():
            members = [r for r in published if r.status.value == value]
            if not members:
                continue
            hub_info = {
                "path": f"status/{value}.html",
                "title": title,
                "count": len(members),
            }
            status_hubs.append(hub_info)
            status_hub_by_val[value] = hub_info
            members_by_status[value] = members

        collection_hubs: list[dict[str, Any]] = []
        collection_hub_by_key: dict[str, dict[str, Any]] = {}
        collection_members = {
            "shark-tank": [r for r in published if is_shark_tank(r)],
            "other-companies": [r for r in published if not is_shark_tank(r)],
        }
        collection_short_labels = {
            "shark-tank": "Shark Tank companies",
            "other-companies": "Other notable companies",
        }
        for key, (title, intro) in COLLECTIONS.items():
            if collection_members[key]:
                hub_info = {
                    "path": f"collections/{key}.html",
                    "title": title,
                    "label": collection_short_labels.get(key, title),
                    "count": len(collection_members[key]),
                }
                collection_hubs.append(hub_info)
                collection_hub_by_key[key] = hub_info
        all_hubs = collection_hubs + status_hubs

        by_episode: dict[tuple[int, int], list[StatusReport]] = {}
        for r in published:
            detail = research_by_name.get(r.company.name.casefold())
            for ep_key in _episode_keys(detail):
                by_episode.setdefault(ep_key, []).append(r)

        def _related_for(r: StatusReport, limit: int = 6) -> list[StatusReport]:
            same_status = [
                cand
                for cand in members_by_status.get(r.status.value, [])
                if cand.company.slug != r.company.slug
            ]
            # Prefer companies in the same collection (Shark Tank vs other)
            r_shark = is_shark_tank(r)
            preferred = [c for c in same_status if is_shark_tank(c) == r_shark]
            others = [c for c in same_status if is_shark_tank(c) != r_shark]
            ordered = preferred + others
            if len(ordered) <= limit:
                return ordered
            # Deterministic window based on company position so links distribute evenly
            idx = next(
                (
                    i
                    for i, cand in enumerate(members_by_status.get(r.status.value, []))
                    if cand.company.slug == r.company.slug
                ),
                0,
            )
            rotated = ordered[idx % len(ordered) :] + ordered[: idx % len(ordered)]
            return rotated[:limit]

        # --- article pages (verified only) -------------------------------- #
        article_tpl = self.env.get_template("article.html")
        written_pages: list[tuple[str, str]] = []
        for r in published:
            detail = research_by_name.get(r.company.name.casefold())
            article_url = (
                f"{self.site_url}/companies/{r.company.slug}.html"
                if self.site_url
                else ""
            )
            c_key = "shark-tank" if is_shark_tank(r) else "other-companies"
            c_hub = collection_hub_by_key.get(c_key)
            s_hub = status_hub_by_val.get(r.status.value)
            ep_companions: list[StatusReport] = []
            seen_ep_slugs = {r.company.slug}
            for ep_key in sorted(_episode_keys(detail)):
                for comp in by_episode.get(ep_key, []):
                    if comp.company.slug not in seen_ep_slugs:
                        ep_companions.append(comp)
                        seen_ep_slugs.add(comp.company.slug)
            related = [
                comp
                for comp in _related_for(r)
                if comp.company.slug not in seen_ep_slugs
            ]
            html = article_tpl.render(
                **self._ctx(
                    report=r,
                    display_summary=r.summary,
                    detail=detail,
                    detail_sources={
                        source["id"]: source
                        for source in (detail or {}).get("sources", [])
                    },
                    research_only=False,
                    noindex=False,
                    rel_root="../",
                    canonical_url=article_url,
                    n_companies=n_companies,
                    jsonld=_jsonld_for(r, self.site_url),
                    breadcrumb_jsonld=_breadcrumb_jsonld(
                        r, self.site_url, c_hub, s_hub, research_only=False
                    ),
                    collection_hub=c_hub,
                    status_hub=s_hub,
                    episode_companions=ep_companions,
                    related_companies=related,
                )
            )
            path = os.path.join(companies_dir, f"{r.company.slug}.html")
            _write(path, html)
            written_pages.append((f"companies/{r.company.slug}.html", r.as_of))

        # Unresolved companies with a substantive research record get a public,
        # noindex evidence page.  It documents blockers without promoting an
        # unverified status into the verified index or sitemap.
        research_only_pages: list[str] = []
        for r in unpublished:
            detail = research_by_name.get(r.company.name.casefold())
            if not detail:
                continue
            article_url = (
                f"{self.site_url}/companies/{r.company.slug}.html"
                if self.site_url
                else ""
            )
            c_key = "shark-tank" if is_shark_tank(r) else "other-companies"
            c_hub = collection_hub_by_key.get(c_key)
            ep_companions = []
            seen_ep_slugs = {r.company.slug}
            for ep_key in sorted(_episode_keys(detail)):
                for comp in by_episode.get(ep_key, []):
                    if comp.company.slug not in seen_ep_slugs:
                        ep_companions.append(comp)
                        seen_ep_slugs.add(comp.company.slug)
            html = article_tpl.render(
                **self._ctx(
                    report=r,
                    display_summary=next(
                        (
                            claim["text"]
                            for claim in detail.get("claims", [])
                            if claim.get("evidence_level") == "unresolved"
                        ),
                        detail.get("claims", [{}])[0].get("text", r.summary)
                        if detail.get("claims")
                        else r.summary,
                    ),
                    detail=detail,
                    detail_sources={
                        source["id"]: source
                        for source in detail.get("sources", [])
                    },
                    research_only=True,
                    noindex=True,
                    rel_root="../",
                    canonical_url=article_url,
                    n_companies=n_companies,
                    jsonld="",
                    breadcrumb_jsonld="",
                    collection_hub=c_hub,
                    status_hub=None,
                    episode_companions=ep_companions,
                    related_companies=[],
                )
            )
            path = os.path.join(companies_dir, f"{r.company.slug}.html")
            _write(path, html)
            research_only_pages.append(f"companies/{r.company.slug}.html")

        # --- hub pages ------------------------------------------------------ #
        hub_tpl = self.env.get_template("hub.html")
        hub_pages: list[tuple[str, str]] = []

        def _render_hub(path: str, title: str, intro: str, members, pending=()):
            url = f"{self.site_url}/{path}" if self.site_url else ""
            html = hub_tpl.render(
                **self._ctx(
                    hub_title=title,
                    hub_intro=intro,
                    members=members,
                    pending=list(pending),
                    hubs=all_hubs,
                    current_path=path,
                    rel_root="../",
                    canonical_url=url,
                    n_companies=n_companies,
                    jsonld=_itemlist_jsonld(title, url, members, self.site_url),
                )
            )
            _write(os.path.join(out_dir, path), html)
            hub_pages.append((path, _latest_as_of(members)))

        for value, (title, intro) in STATUS_HUB_LABELS.items():
            members = members_by_status.get(value, [])
            if members:
                _render_hub(f"status/{value}.html", title, intro, members)
        for key, (title, intro) in COLLECTIONS.items():
            members = collection_members[key]
            if not members:
                continue
            pending = (
                [
                    r
                    for r in unpublished
                    if is_shark_tank(r)
                    and r.company.name.casefold() in research_by_name
                ]
                if key == "shark-tank"
                else []
            )
            _render_hub(f"collections/{key}.html", title, intro, members, pending)

        # --- index --------------------------------------------------------- #
        index_html = self.env.get_template("index.html").render(
            **self._ctx(
                published=published,
                unpublished=unpublished,
                stats=result.summary(),
                rel_root="",
                canonical_url=root_url,
                episode_primary=episode_primary,
                episode_second_tier=episode_second_tier,
                research_slugs={
                    r.company.slug
                    for r in unpublished
                    if r.company.name.casefold() in research_by_name
                },
                n_companies=n_companies,
                status_hubs=status_hubs,
                collection_hubs=collection_hubs,
                jsonld=_website_jsonld(
                    self.site_name,
                    self.site_description,
                    self.site_url,
                    len(published),
                ),
            )
        )
        _write(os.path.join(out_dir, "index.html"), index_html)

        # --- methodology --------------------------------------------------- #
        methodology_url = (
            f"{self.site_url}/methodology.html" if self.site_url else ""
        )
        method_html = self.env.get_template("methodology.html").render(
            **self._ctx(
                rel_root="",
                canonical_url=methodology_url,
                n_companies=n_companies,
                jsonld=_webpage_jsonld(
                    f"Verification Methodology — How We Determine Company Status | {self.site_name}",
                    (
                        "How Defunct Company Tracker verifies whether Shark Tank and "
                        "notable companies are active, acquired, or defunct."
                    ),
                    methodology_url,
                    self.site_name,
                    self.site_url,
                ),
            )
        )
        _write(os.path.join(out_dir, "methodology.html"), method_html)

        # --- 404 page ------------------------------------------------------ #
        if os.path.exists(os.path.join(self.template_dir, "404.html")):
            not_found_html = self.env.get_template("404.html").render(
                **self._ctx(
                    rel_root="/",
                    canonical_url="",
                    noindex=True,
                    n_companies=n_companies,
                )
            )
            _write(os.path.join(out_dir, "404.html"), not_found_html)

        # --- sitemap ------------------------------------------------------- #
        latest = _latest_as_of(published)
        self._write_sitemap(
            out_dir,
            [
                ("", latest),
                ("methodology.html", latest),
                *hub_pages,
                *written_pages,
            ],
        )
        self._write_robots(out_dir)

        return {
            "pages": len(written_pages) + len(research_only_pages) + len(hub_pages) + 2,
            "articles": len(written_pages),
            "research_only": len(research_only_pages),
            "withheld": len(unpublished),
            "hubs": len(hub_pages),
        }

    def _write_sitemap(
        self, out_dir: str, entries: Iterable[str | tuple[str, str]]
    ) -> None:
        """Write sitemap.xml. Entries are paths or ``(path, lastmod)`` pairs;
        an empty path means the site root. ``lastmod`` comes from the research
        ``as_of`` date and is omitted when it is not a valid W3C date."""
        from xml.sax.saxutils import escape

        base = self.site_url or ""
        lines = ['<?xml version="1.0" encoding="UTF-8"?>']
        lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
        for entry in entries:
            p, lastmod = (entry, "") if isinstance(entry, str) else entry
            loc = f"{base}/{p}" if base else (p or "index.html")
            lm = _w3c_date(lastmod)
            lm_xml = f"<lastmod>{lm}</lastmod>" if lm else ""
            lines.append(f"  <url><loc>{escape(loc)}</loc>{lm_xml}</url>")
        lines.append("</urlset>")
        _write(os.path.join(out_dir, "sitemap.xml"), "\n".join(lines) + "\n")

    def _write_robots(self, out_dir: str) -> None:
        lines = ["User-agent: *", "Allow: /"]
        if self.site_url:
            lines.append(f"Sitemap: {self.site_url}/sitemap.xml")
        _write(os.path.join(out_dir, "robots.txt"), "\n".join(lines) + "\n")


_W3C_DATE_RE = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")


def _w3c_date(value: str | None) -> str:
    """Return ``value`` if it is a W3C date (YYYY, YYYY-MM or YYYY-MM-DD)."""
    value = (value or "").strip()
    return value if _W3C_DATE_RE.match(value) else ""


def _latest_as_of(reports: Iterable[StatusReport]) -> str:
    """Latest full ``YYYY-MM-DD`` as_of date among ``reports`` (or "")."""
    dates = [r.as_of for r in reports if re.match(r"^\d{4}-\d{2}-\d{2}$", r.as_of or "")]
    return max(dates) if dates else ""


def _itemlist_jsonld(
    title: str, url: str, members: Iterable[StatusReport], site_url: str
) -> str:
    items = []
    for i, r in enumerate(members, start=1):
        item: dict[str, Any] = {"@type": "ListItem", "position": i, "name": r.company.name}
        if site_url:
            item["url"] = f"{site_url}/companies/{r.company.slug}.html"
        items.append(item)
    node: dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": title,
        "numberOfItems": len(items),
        "itemListElement": items,
    }
    if url:
        node["url"] = url
    return _json_for_script(node)


def _write(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
