# Open-Source Synthetic Data Proportion Analysis

Analyzing synthetic data usage in pretraining across flagship open-source LLMs released since Jan 2024.

**Goal**: Build a chart showing "synthetic tokens per parameter" (TPP) for web vs. synthetic tokens across open-weight models.

**Methodology**:
1. Catalog all flagship open-source model releases since Jan 1, 2024
2. Pull technical reports and extract: total training tokens, synthetic token counts, web token counts
3. Compute TPP using active params (for MoE) or total params (for dense)
4. Visualize the landscape

**Status**: Phase 1 (catalog) complete. Phase 2 (technical report analysis) pending.

## Files

- `model-catalog.md` — Comprehensive catalog of open-source model releases
- (Phase 2) `synthetic-analysis.md` — Extracted synthetic data proportions from tech reports
- (Phase 2) `tpp-chart.py` — Visualization script
