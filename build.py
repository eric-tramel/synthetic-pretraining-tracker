# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Build index.html from template.html + data/models.yaml + data/authors.yaml."""

import json
import yaml
from pathlib import Path

ROOT = Path(__file__).parent
MODELS_DATA = ROOT / "data" / "models.yaml"
AUTHORS_DATA = ROOT / "data" / "authors.yaml"
TEMPLATE = ROOT / "template.html"
OUT = ROOT / "index.html"


def build():
    with open(MODELS_DATA) as f:
        models = yaml.safe_load(f)

    with open(AUTHORS_DATA) as f:
        authors = yaml.safe_load(f)

    with open(TEMPLATE) as f:
        template = f.read()

    model_json = json.dumps(models, indent=2, ensure_ascii=False)
    authors_json = json.dumps(authors, indent=2, ensure_ascii=False)
    html = template.replace("%%MODEL_DATA%%", model_json)
    html = html.replace("%%AUTHOR_DATA%%", authors_json)

    with open(OUT, "w") as f:
        f.write(html)
        f.write("\n")

    print(f"Built {OUT} with {len(models)} models, {len(authors)} authors")


if __name__ == "__main__":
    build()
