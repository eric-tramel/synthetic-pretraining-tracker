# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Build site/ from template.html + data/models.yaml + data/authors.yaml."""

import json
import shutil
import yaml
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).parent
MODELS_DATA = ROOT / "data" / "models.yaml"
AUTHORS_DATA = ROOT / "data" / "authors.yaml"
TEMPLATE = ROOT / "template.html"
SITE = ROOT / "site"

BASE_URL = "https://eric-tramel.github.io/synthetic-pretraining-tracker"
REPO_URL = "https://github.com/eric-tramel/synthetic-pretraining-tracker"


def fmt(n):
    """Format params/active as B/T. Matches JS fmt()."""
    if n is None:
        return ""
    if n >= 1000:
        v = f"{n / 1000:.1f}".removesuffix(".0")
        return v + "T"
    v = f"{n:.1f}".removesuffix(".0")
    return v + "B"


def fmt_tokens(n):
    """Format token counts. Matches JS fmtTokens() — no decimal for <1000."""
    if n is None:
        return ""
    if n >= 1000:
        v = f"{n / 1000:.1f}".removesuffix(".0")
        return v + "T"
    # JS: n + 'B' (no toFixed)
    # n could be int or float from YAML; match JS Number coercion
    if isinstance(n, float) and n == int(n):
        return f"{int(n)}B"
    return f"{n}B"


def arch_badge(arch):
    """Render architecture badge. Matches JS archBadge()."""
    if arch == "dense":
        cls, label = "arch-dense", "Dense"
    elif arch == "moe":
        cls, label = "arch-moe", "MoE"
    else:
        cls, label = "arch-hybrid", "Hybrid"
    return f'<span class="arch-badge {cls}">{label}</span>'


def _cite_tooltip(cite):
    """Build a cite-wrap span with tooltip. Used for tokens and synth_tokens."""
    quote_html = escape(cite["quote"])
    source_html = escape(cite["source"])
    url = escape(cite["url"], quote=True)
    return (
        f'<div class="cite-tooltip">'
        f'<div class="cite-quote">{quote_html}</div>'
        f'<div class="cite-source">'
        f'<a href="{url}" target="_blank">{source_html}</a>'
        f"</div></div>"
    )


def render_row(m):
    """Render a single <tr> for model m. Matches JS renderTable() row logic."""
    undisclosed = '<span class="tbd">undisclosed</span>'

    tokens = m.get("tokens")
    params = m.get("params")
    active = m.get("active")
    synth_tokens = m.get("synth_tokens")
    tokens_cite = m.get("tokens_cite")
    synth_cite = m.get("synth_cite")
    synth_note = m.get("synth_note")
    report = m.get("report")
    report_label = m.get("report_label")

    # Computed values (match JS exactly)
    tpp = f"{tokens / params:.1f}" if tokens and params else None
    stpp = (
        f"{synth_tokens / params:.1f}"
        if synth_tokens is not None and params
        else None
    )
    synth_pct = (
        f"{synth_tokens / tokens * 100:.1f}"
        if synth_tokens is not None and tokens
        else None
    )

    # Report link
    if report:
        label = escape(report_label) if report_label else "PDF"
        report_link = (
            f'<a href="{escape(report, quote=True)}" '
            f'class="report-link" target="_blank">{label}</a>'
        )
    else:
        report_link = '<span class="tbd">none</span>'

    # Tokens cell
    if not tokens:
        tokens_cell = undisclosed
    elif tokens_cite:
        tokens_cell = (
            f'<span class="cite-wrap">{fmt_tokens(tokens)}'
            f"{_cite_tooltip(tokens_cite)}</span>"
        )
    else:
        tokens_cell = fmt_tokens(tokens)

    # TPP cell
    tpp_cell = tpp if tpp is not None else "" if tokens else undisclosed

    # Synth tokens cell
    if not tokens:
        synth_tokens_cell = undisclosed
    elif synth_tokens is not None and synth_cite:
        val = (
            '<span class="zero">0</span>'
            if synth_tokens == 0
            else fmt_tokens(synth_tokens)
        )
        synth_tokens_cell = (
            f'<span class="cite-wrap">{val}'
            f"{_cite_tooltip(synth_cite)}</span>"
        )
    elif synth_tokens == 0:
        synth_tokens_cell = '<span class="zero">0</span>'
    elif synth_tokens is not None:
        synth_tokens_cell = fmt_tokens(synth_tokens)
    else:
        synth_tokens_cell = '<span class="tbd">TBD</span>'

    # STPP cell
    if not tokens:
        stpp_cell = undisclosed
    elif synth_tokens == 0:
        stpp_cell = '<span class="zero">0</span>'
    elif stpp is not None:
        stpp_cell = stpp
    else:
        stpp_cell = '<span class="tbd">TBD</span>'

    # Synth % cell
    if not tokens:
        synth_pct_cell = undisclosed
    elif synth_tokens == 0:
        synth_pct_cell = '<span class="zero">0%</span>'
    elif synth_pct is not None:
        synth_pct_cell = f'<span class="bar-cell">{synth_pct}%</span>'
    else:
        synth_pct_cell = '<span class="tbd">TBD</span>'

    # Active params always shows the number
    active_cell = fmt(active)

    # synth_note title attribute (only when no synth_cite)
    synth_title = ""
    if synth_note and not synth_cite:
        synth_title = f' title="{escape(synth_note, quote=True)}"'

    name_html = escape(m["name"])
    url_html = escape(m["url"], quote=True)
    org_html = escape(m["org"])
    date_html = escape(str(m["date"]))

    return (
        "<tr>\n"
        f'      <td><a href="{url_html}" target="_blank">{name_html}</a></td>\n'
        f"      <td>{report_link}</td>\n"
        f"      <td>{org_html}</td>\n"
        f"      <td>{date_html}</td>\n"
        f"      <td>{arch_badge(m['arch'])}</td>\n"
        f'      <td class="num">{fmt(params)}</td>\n'
        f'      <td class="num">{active_cell}</td>\n'
        f'      <td class="num">{tokens_cell}</td>\n'
        f'      <td class="num">{tpp_cell}</td>\n'
        f'      <td class="num"{synth_title}>{synth_tokens_cell}</td>\n'
        f'      <td class="num"{synth_title}>{stpp_cell}</td>\n'
        f'      <td class="num"{synth_title}>{synth_pct_cell}</td>\n'
        "    </tr>"
    )


def render_table_rows(models):
    """Render all rows, sorted by date ascending (matches JS initial render)."""
    sorted_models = sorted(
        models,
        key=lambda m: (m.get("date") is None, m.get("date", "")),
    )
    return "\n".join(render_row(m) for m in sorted_models)


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
    table_rows = render_table_rows(models)
    html = template.replace("%%TABLE_ROWS%%", table_rows)
    html = html.replace("%%MODEL_DATA%%", model_json)
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
