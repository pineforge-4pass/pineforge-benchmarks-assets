# Legal — PineForge Benchmark Assets

This repository ships the per-strategy fixtures and OHLCV snapshot used by the [`pineforge-engine/benchmarks/`](https://github.com/fullpass-4pass/pineforge-engine/tree/main/benchmarks) three-way reproducer (PineForge ↔ PyneCore ↔ PineTS). It is mounted into the engine repo as the `benchmarks/assets` git submodule.

Public reproduction of the bench requires this submodule. License: **Apache-2.0** (same as the engine runtime).

## Contents

- `data/ETHUSDT_15.csv` — Binance USDT-M futures ETH/USDT-USDT 15-minute OHLCV, 53,930 bars (2024-10-20 → 2026-05-04). Public market price/volume series — factual data, not copyrightable in the US/EU.
- `strategies/<NN-slug>/strategy.pine` — clean-room PineScript v6 sources authored by PineForge contributors. Each carries an Apache-2.0 SPDX header (`// SPDX-License-Identifier: Apache-2.0`) and a brief purpose comment. Same authorship + license as the public corpus probes under [`pineforge-engine/corpus/validation/`](https://github.com/fullpass-4pass/pineforge-engine/tree/main/corpus/validation).
- `strategies/<NN-slug>/generated.cpp` — codegen output of the corresponding `strategy.pine`. Inherits the `.pine` Apache-2.0 license. Committed so public users can build `strategy.dylib` via `cmake --build build --target bench_strategies` without needing the closed-source codegen.
- `strategies/<NN-slug>/strategy_pyne.py` — mechanical translation of `strategy.pine` produced by the [PyneSys cloud compiler](https://pynesys.io/) (`pyne compile`, PyneComp v6.4.6). Derivative work of the underlying `.pine`; inherits its Apache-2.0 license. The PyneSys compiler is a tool (like `gcc`); its output does not transfer copyright to the vendor.
- `strategies/<NN-slug>/tv_trades.csv` — TradingView's "List of Trades" export from the broker emulator running the same `strategy.pine` against the same OHLCV. We hold the right to redistribute these as artifacts of running our own scripts.
- `strategies/<NN-slug>/pineforge_trades.csv`, `pynecore_trades.csv` — engine outputs in TV-format for direct line-by-line parity comparison. Apache-2.0.
- `strategies/<NN-slug>/inputs.json` (selective) — engine `runtime_overrides` (bar magnifier mode), `ohlcv_start_ms` (warmup trim), parity profile / tier overrides. Apache-2.0.
- `strategies/_indicators/canonical.pine` + cloud-compiled `canonical_pyne.py` + per-engine `canonical_*.csv` — 10-indicator canonical script + outputs for the per-bar indicator comparator. Same license as the strategies above.
- `strategies/CMakeLists.txt` — per-strategy build config consumed by `pineforge-engine`'s root CMake when `-DPINEFORGE_BUILD_BENCH_STRATEGIES=ON` is passed. Apache-2.0.

## Redistribution

All files above are redistributable under Apache-2.0 either directly (engine code, scripts, CMakeLists) or by the same logic the corpus uses (clean-room `.pine` + their derivative artifacts; TV-export of running our own scripts; public market data).

If you fork this repo and add probes from third-party PineScript (community library, paid-script vendor, etc.), those probes are governed by their original license — clear them independently before publishing.

## Trademarks

TradingView, PineScript, PyneCore, and PineTS are marks of their respective projects. No affiliation is implied.

## Linked engine + tooling

- Engine runtime: [`pineforge-engine`](https://github.com/fullpass-4pass/pineforge-engine) (Apache-2.0)
- Closed-source codegen (not required to reproduce): `pineforge-codegen`
- PyneCore runtime: [`PyneSys/pynecore`](https://github.com/PyneSys/pynecore) (Apache-2.0)
- PineTS runtime: [`LuxAlgo/PineTS`](https://github.com/LuxAlgo/PineTS) (AGPL-3.0). Linked at run time only; we publish numerical results, not PineTS source.

This file is guidance, not legal advice.
