# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Build site/ from template.html + data/models.yaml + data/authors.yaml."""

import json
import shutil
import yaml
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
MODELS_DATA = ROOT / "data" / "models.yaml"
AUTHORS_DATA = ROOT / "data" / "authors.yaml"
TEMPLATE = ROOT / "template.html"
SITE = ROOT / "site"

BASE_URL = "https://eric-tramel.github.io/synthetic-pretraining-tracker"
REPO_URL = "https://github.com/eric-tramel/synthetic-pretraining-tracker"


def build():
    with open(MODELS_DATA) as f:
        models = yaml.safe_load(f)

    with open(AUTHORS_DATA) as f:
        authors = yaml.safe_load(f)

    with open(TEMPLATE) as f:
        template = f.read()

    # Prepare site directory
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()
    (SITE / "data").mkdir()

    # Build HTML
    today = date.today()
    build_date = today.strftime("%B %d, %Y")
    build_date_iso = today.isoformat()
    model_json = json.dumps(models, indent=2, ensure_ascii=False)
    authors_json = json.dumps(authors, indent=2, ensure_ascii=False)
    html = template.replace("%%MODEL_DATA%%", model_json)
    html = html.replace("%%AUTHOR_DATA%%", authors_json)
    html = html.replace("%%BUILD_DATE%%", build_date)
    html = html.replace("%%BUILD_DATE_ISO%%", build_date_iso)

    (SITE / "index.html").write_text(html + "\n")

    # Social card (1200x630 SVG rendered as PNG-compatible)
    n_models = len(models)
    n_with_synth = sum(1 for m in models if m.get("synth_tokens") is not None)
    n_with_tokens = sum(1 for m in models if m.get("tokens") is not None)
    social_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <rect width="1200" height="630" fill="#0d1117"/>
  <text x="80" y="180" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="52" font-weight="700" fill="#e6edf3">Tracker: Synthetic Data</text>
  <text x="80" y="245" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="52" font-weight="700" fill="#e6edf3">in Pretraining</text>
  <text x="80" y="320" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="24" fill="#8b949e">Open-weight LLMs since Jan 2024 — cited token counts &amp; synthetic data proportions</text>
  <text x="80" y="430" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="36" fill="#58a6ff">{n_models} models</text>
  <text x="380" y="430" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="36" fill="#3fb950">{n_with_tokens} with token counts</text>
  <text x="780" y="430" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="36" fill="#d29922">{n_with_synth} with synth data</text>
  <text x="80" y="560" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="20" fill="#8b949e">eric-tramel.github.io/synthetic-pretraining-tracker</text>
  <line x1="80" y1="480" x2="1120" y2="480" stroke="#30363d" stroke-width="1"/>
</svg>'''
    (SITE / "social-card.svg").write_text(social_svg)

    # Data exports
    shutil.copy(MODELS_DATA, SITE / "data" / "models.yaml")
    shutil.copy(AUTHORS_DATA, SITE / "data" / "authors.yaml")
    (SITE / "data" / "models.json").write_text(
        json.dumps(models, indent=2, ensure_ascii=False) + "\n"
    )

    # llms.txt
    llms_txt = f"""# Synthetic Pretraining Tracker
# Tracking synthetic data usage in open-weight LLM pretraining (Jan 2024+)

> {BASE_URL}/
> {BASE_URL}/data/models.json
> {BASE_URL}/data/models.yaml
> {BASE_URL}/data/authors.yaml
> {REPO_URL}

## Fields

Each model entry contains:
- name: Model name
- url: HuggingFace model card URL
- report: Technical report URL (PDF, blog, or paper)
- org: Organization
- date: Release date (YYYY-MM)
- arch: Architecture (dense, moe, hybrid)
- params: Total parameters in billions
- active: Active parameters in billions (same as params for dense)
- tokens: Total pretraining tokens in billions (null if undisclosed)
- tokens_cite: Direct quote and source for token count
- synth_tokens: Synthetic pretraining tokens in billions (null if unknown)
- synth_cite: Direct quote and source for synthetic token count
- synth_note: Brief context on synthetic data status
"""
    (SITE / "llms.txt").write_text(llms_txt)

    # robots.txt
    robots_txt = f"""User-agent: *
Allow: /

Sitemap: {BASE_URL}/sitemap.xml
"""
    (SITE / "robots.txt").write_text(robots_txt)

    # sitemap.xml
    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{BASE_URL}/</loc>
    <lastmod>{build_date_iso}</lastmod>
    <changefreq>weekly</changefreq>
  </url>
  <url>
    <loc>{BASE_URL}/data/models.json</loc>
    <lastmod>{build_date_iso}</lastmod>
    <changefreq>weekly</changefreq>
  </url>
  <url>
    <loc>{BASE_URL}/data/models.yaml</loc>
    <lastmod>{build_date_iso}</lastmod>
    <changefreq>weekly</changefreq>
  </url>
  <url>
    <loc>{BASE_URL}/llms.txt</loc>
    <lastmod>{build_date_iso}</lastmod>
    <changefreq>monthly</changefreq>
  </url>
</urlset>
"""
    (SITE / "sitemap.xml").write_text(sitemap)

    print(f"Built site/ with {len(models)} models, {len(authors)} authors")
    for f in sorted(SITE.rglob("*")):
        if f.is_file():
            print(f"  {f.relative_to(ROOT)}")


if __name__ == "__main__":
    build()
