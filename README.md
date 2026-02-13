# Synthetic Pretraining Tracker

Tracking synthetic data usage in open-weight LLM pretraining, from Jan 2024 onward.

**Live site**: [eric-tramel.github.io/synthetic-pretraining-tracker](https://eric-tramel.github.io/synthetic-pretraining-tracker/)

## What this is

A sortable, cited table of open-weight language models with:

- Total pretraining token counts (with direct quotes from technical reports)
- Synthetic pretraining token counts where disclosed
- Tokens-per-parameter (TPP) and synthetic tokens-per-parameter (STPP) ratios
- Links to model cards and technical reports

Every number has a hover tooltip showing the exact quote and source. If a number isn't publicly confirmed, it says so.

## How it works

Model data lives in `data/models.yaml`. A build script reads the YAML and a HTML template to produce a static page:

```
data/models.yaml + data/authors.yaml + template.html → build.py → index.html
```

```bash
uv run build.py        # build locally
make build             # or via make
```

GitHub Actions builds and deploys to Pages on every push to `main`.

## Project structure

```
data/
  models.yaml          # model entries (the source of truth)
  authors.yaml         # author names and X handles
template.html          # HTML/CSS/JS template
build.py               # YAML → HTML build script
Makefile               # build/clean targets
.github/workflows/     # CI: build + deploy to GitHub Pages
```

## Contributing

Contributions are welcome. To add a model or correct data, open a pull request that updates:

1. **`data/models.yaml`** with the new or corrected model entry. Each entry needs:
   - `name`, `url` (HuggingFace model card), `org`, `date` (YYYY-MM), `arch` (dense/moe/hybrid)
   - `params` (total, in billions), `active` (active params, in billions)
   - `tokens` (pretraining tokens, in billions — so 15.6T = 15600)
   - `tokens_cite` with `quote` (direct quote from source), `source` (paper/blog reference), `url`
   - `synth_tokens` (synthetic pretraining tokens in billions, or `null` if unknown)
   - `synth_cite` with quote/source/url if synth_tokens is provided
   - `synth_note` (brief context)
   - `report` (link to tech report PDF or blog) and `report_label` (PDF/blog/paper/github/HF)

2. **`data/authors.yaml`** with your name and X handle (optional).

### Guidelines

- Every token count must have a direct quote from a primary source (tech report, model card, or official blog post). No estimates or inferences.
- If a report doesn't mention synthetic data, set `synth_tokens: null` and explain in `synth_note`. Don't assume zero.
- Use the existing entries as formatting examples.
- Run `uv run build.py` locally to verify your changes produce valid output before submitting.

## License

Data and code in this repository are available under [MIT](LICENSE).
