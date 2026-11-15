# Regime Shift Lab

**When stocks and bonds fall together, does ETF rotation still diversify risk?**

A reproducible quantitative research project by Youssef Mir, motivated by the IMF's February 2026 analysis of weaker stock–bond diversification. A fixed, transparent momentum/correlation rule rotates among US equity, Treasury and gold ETFs and is compared with a monthly 60/40 benchmark.

- Daily portfolio accounting with drift, next-close execution and costs on both trade legs.
- Chronological development / validation / evaluation windows, sensitivity analysis and a filter ablation.
- Interactive research dashboard with equity, drawdown, correlation and methodology.
- Tests for future-data leakage, execution timing, turnover fees and invalid prices.
- TypeSafe Jev 1.14 macro-text classification through the native System One API; probabilities are validated and kept separate from the backtest.

## Reproduce (Python 3.12+)

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/download.py --end 2026-11-15
python -m unittest discover -s tests -v
python src/backtest.py
python -m http.server 8080 --directory site
```

Open http://localhost:8080. Downloads stop before the exclusive end date. The snapshot manifest records coverage and hash. Raw vendor prices are intentionally not committed; rerun the download to regenerate them. Derived results are versioned in `site/results.json` and `reports/`.

Read the [research protocol and limitations](docs/methodology.md). This is a retrospective research exercise, with no order execution or brokerage connection. No claim of live alpha, prospective validation or investment recommendation.

## Structure

`src/download.py` → adjusted daily closes and manifest. `src/backtest.py` → signals, self-financing simulation and reporting. `tests/` → accounting and causality checks. `site/` → standalone dashboard. `docs/` → protocol and Jev integration.

## Source

[IMF, 18 February 2026 — Stock-Bond Diversification Offers Less Protection From Market Selloffs](https://www.imf.org/en/blogs/articles/2026/02/18/stock-bond-diversification-offers-less-protection-from-market-selloffs).
