# Legal - PineForge Benchmark Fixtures (Private)

This repository is not a public distribution. It holds OHLCV snapshots and
per-strategy folders used only with maintainer access.

## Contents

- `data/`: pinned extended OHLCV (for example, Binance ETH/USDT 15m) for
  benchmark reproducibility.
- `strategies/`: per-strategy Pine sources, `tv_trades.csv`, engine/Pyne/PineTS
  trade lists, cloud-compiled Pyne output, and `_indicators/` artefacts.

## Redistribution

1. TradingView-linked CSVs (`tv_trades.csv`, related exports): confidential
   validation data for internal / maintainer use. Do not publish in a public
   default branch without independent legal clearance.
2. `.pine` sources: may be written in-house, sourced from community examples
   under their terms, or aligned with corpus entries; each folder may have
   different underlying rights. Aggregate redistribution needs review.
3. `strategy_pyne.py`: mechanical output from the PyneSys cloud compiler;
   license follows the underlying `strategy.pine` and your agreement with
   PyneSys for generated code.

## Optional SPDX

Use `LicenseRef-Proprietary` or `NONE` for the bundle as a whole unless counsel
specifies otherwise.

## Trademarks

TradingView, PineScript, PyneCore, and PineTS are marks of their respective
projects. No affiliation is implied.

This file is guidance only, not legal advice.
