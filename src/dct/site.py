"""Static site generator.

Renders the verified status reports into a self-contained static website:

    out/
      index.html            (table of verified companies + collapsed unverified)
      methodology.html       (how statuses are determined / verified)
      companies/<slug>.html  (one article per VERIFIED company)
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
import shutil
from datetime import datetime, timezone
from typing import Iterable

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .models import Status, StatusReport
from .pipeline import PipelineResult

_PKG_DIR = os.path.dirname(os.path.abspath(__file__))
# templates/static are shipped INSIDE the package so the generator works both
# from a source checkout and from an installed wheel.
DEFAULT_TEMPLATE_DIR = os.path.join(_PKG_DIR, "templates")
DEFAULT_STATIC_DIR = os.path.join(_PKG_DIR, "static")


def _jsonld_for(report: StatusReport, site_url: str) -> str:
    """An Organization schema.org node describing the company + status."""
    node = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": report.company.name,
        "description": report.summary,
        "dissolutionDate": report.as_of
        if report.status in {Status.DEFUNCT, Status.BANKRUPT} and report.as_of
        else None,
        "url": report.company.domain,
        "alternateName": list(report.company.aliases) or None,
        "subjectOf": [
            {"@type": "WebPage", "url": c.url, "name": c.title}
            for c in report.citations
        ]
        or None,
    }
    node = {k: v for k, v in node.items() if v is not None}
    return _json_for_script(node)


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
    ) -> None:
        self.site_name = site_name
        self.site_description = site_description
        self.site_url = site_url.rstrip("/")
        self.static_dir = static_dir
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
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        }
        base.update(extra)
        return base

    def build(self, result: PipelineResult, out_dir: str) -> dict[str, int]:
        os.makedirs(out_dir, exist_ok=True)
        companies_dir = os.path.join(out_dir, "companies")
        os.makedirs(companies_dir, exist_ok=True)
        assets_dir = os.path.join(out_dir, "assets")
        os.makedirs(assets_dir, exist_ok=True)

        # copy static assets
        if os.path.isdir(self.static_dir):
            for fn in os.listdir(self.static_dir):
                shutil.copy2(
                    os.path.join(self.static_dir, fn), os.path.join(assets_dir, fn)
                )

        published = result.publishable
        unpublished = result.unpublishable
        n_companies = len(result.reports)
        root_url = f"{self.site_url}/" if self.site_url else ""
        published_by_slug = {r.company.slug: r for r in published}
        episode_primary = published_by_slug.get("fish-fixe")
        episode_second_tier = [
            published_by_slug[slug]
            for slug in ("hello-prenup", "deux", "hidrent")
            if slug in published_by_slug
        ]

        # --- article pages (verified only) -------------------------------- #
        article_tpl = self.env.get_template("article.html")
        written_pages: list[str] = []
        for r in published:
            article_url = (
                f"{self.site_url}/companies/{r.company.slug}.html"
                if self.site_url
                else ""
            )
            html = article_tpl.render(
                **self._ctx(
                    report=r,
                    rel_root="../",
                    canonical_url=article_url,
                    n_companies=n_companies,
                    jsonld=_jsonld_for(r, self.site_url),
                )
            )
            path = os.path.join(companies_dir, f"{r.company.slug}.html")
            _write(path, html)
            written_pages.append(f"companies/{r.company.slug}.html")

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
                n_companies=n_companies,
            )
        )
        _write(os.path.join(out_dir, "index.html"), index_html)

        # --- methodology --------------------------------------------------- #
        methodology_url = (
            f"{self.site_url}/methodology.html" if self.site_url else ""
        )
        method_html = self.env.get_template("methodology.html").render(
            **self._ctx(
                rel_root="", canonical_url=methodology_url, n_companies=n_companies
            )
        )
        _write(os.path.join(out_dir, "methodology.html"), method_html)

        # --- sitemap ------------------------------------------------------- #
        self._write_sitemap(out_dir, ["index.html", "methodology.html", *written_pages])
        self._write_robots(out_dir)

        return {
            "pages": len(written_pages) + 2,
            "articles": len(written_pages),
            "withheld": len(unpublished),
        }

    def _write_sitemap(self, out_dir: str, paths: Iterable[str]) -> None:
        base = self.site_url or ""
        lines = ['<?xml version="1.0" encoding="UTF-8"?>']
        lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
        for p in paths:
            loc = f"{base}/{p}" if base else p
            lines.append(f"  <url><loc>{loc}</loc></url>")
        lines.append("</urlset>")
        _write(os.path.join(out_dir, "sitemap.xml"), "\n".join(lines) + "\n")

    def _write_robots(self, out_dir: str) -> None:
        lines = ["User-agent: *", "Allow: /"]
        if self.site_url:
            lines.append(f"Sitemap: {self.site_url}/sitemap.xml")
        _write(os.path.join(out_dir, "robots.txt"), "\n".join(lines) + "\n")


def _write(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
