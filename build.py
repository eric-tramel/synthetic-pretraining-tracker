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
    build_date = date.today().strftime("%B %d, %Y")
    model_json = json.dumps(models, indent=2, ensure_ascii=False)
    authors_json = json.dumps(authors, indent=2, ensure_ascii=False)
    html = template.replace("%%MODEL_DATA%%", model_json)
    html = html.replace("%%AUTHOR_DATA%%", authors_json)
    html = html.replace("%%BUILD_DATE%%", build_date)

    (SITE / "index.html").write_text(html + "\n")

    # Data exports
    shutil.copy(MODELS_DATA, SITE / "data" / "models.yaml")
    (SITE / "data" / "models.json").write_text(
        json.dumps(models, indent=2, ensure_ascii=False) + "\n"
    )

    # llms.txt
    llms_txt = f"""# Synthetic Pretraining Tracker
# Tracking synthetic data usage in open-weight LLM pretraining (Jan 2024+)

> {BASE_URL}/
> {BASE_URL}/data/models.json
> {BASE_URL}/data/models.yaml
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

    print(f"Built site/ with {len(models)} models, {len(authors)} authors")
    print(f"  site/index.html")
    print(f"  site/data/models.yaml")
    print(f"  site/data/models.json")
    print(f"  site/llms.txt")


if __name__ == "__main__":
    build()
