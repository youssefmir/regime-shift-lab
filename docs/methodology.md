# Research protocol

## Question

Can a transparent correlation-aware ETF rotation improve the downside profile of a monthly rebalanced 60/40 SPY/IEF portfolio?

Motivation: the IMF's 18 February 2026 article, “Stock-Bond Diversification Offers Less Protection From Market Selloffs”, discusses weaker stock–bond hedging. This motivates a hypothesis; it does not establish this strategy's effectiveness.

Source: https://www.imf.org/en/blogs/articles/2026/02/18/stock-bond-diversification-offers-less-protection-from-market-selloffs

## Rules

- Universe fixed in advance: SPY (US equities), IEF (7–10-year US Treasuries), GLD (gold), SHY (short US Treasuries). USD. SHY is an invested ETF, not risk-free cash.
- At each month-end, calculate 126-trading-day price momentum, 63-day daily-return volatility and 63-day SPY/IEF daily-return correlation.
- If correlation is positive, exclude IEF. Rank SPY/IEF/GLD by momentum, retain at most two assets with positive momentum and weight them by inverse volatility. If none qualify, allocate to SHY.
- Signals use the month-end close. Execute at the next trading day's close. New holdings earn returns only after that close. This deliberately imposes an extra execution lag.
- Holdings drift between monthly trades. Charge 10 bps on traded notional, on both buy and sell legs. A full replacement has turnover 2.0. Initial purchase has turnover 1.0. Fees reduce equity before new allocation; turnover is approximated using pre-fee weights.
- No shorting, leverage, leverage financing, derivative exposures or real orders.
- Benchmark: SPY 60% / IEF 40%, same monthly execution calendar and costs.

## Evaluation

The study is designed retrospectively in November 2026. Development (2007–2017), validation (2018–2021), and evaluation (2022–latest available) are chronological reporting windows, not a truly untouched prospective holdout. No parameter optimizer selects the winning variant. The fixed 126/63/63-day rule is reported even if it underperforms. Sensitivity: 63/126/252-day momentum and 0/10/25 bps costs. Ablation: remove the correlation filter.

Metrics: compound annual growth rate, annualized daily volatility, maximum drawdown and annualized Sharpe with zero reference rate (explicitly not an excess-return Sharpe against T-bills). Subperiod metrics rebase at the first close of each window. Monthly returns omit the first incomplete month. Initial fees are included in the full equity path; if there is no preceding observation, first-close normalization excludes that initial fee from summary metrics.

## Data and limits

Yahoo Finance adjusted closes downloaded using yfinance. The dated snapshot has a SHA-256 manifest. Adjusted-close execution is a total-return approximation; a production system would model shares, unadjusted opens/closes, splits, distributions and cash separately. ETF expenses are embedded in market returns; no additional management charge. Transaction-cost assumptions are stylized and exclude market impact, taxes, FX, spread changes and cash interest before initial deployment.

The four surviving ETFs and the research question were chosen with hindsight. Correlation is noisy and lagging. Neither current news nor past performance proves tradable alpha. Results are research simulations, not live or guaranteed performance. Market-data redistribution is subject to the provider's terms; only derived research outputs are published, with raw prices kept local.
