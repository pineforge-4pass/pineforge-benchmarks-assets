# PineForge Benchmark Assets

Benchmark fixtures for the PineForge engine.

This repository is mounted into the engine checkout as the `benchmarks/assets`
git submodule. It ships TradingView-linked validation data: each slot's
`tv_trades.csv` is a TradingView "List of Trades" export (see `LEGAL.md`).

## Layout

```text
data/
  ETHUSDT_15.csv
strategies/
  001-analyzer-anvil-percent-costs-01/
  ...
  100-vwap-bands-mean-reversion-2sigma-01/
  _indicators/
  CMakeLists.txt
```

The 100 slots are probes of the public PineForge corpus
([`pineforge-corpus`](https://github.com/pineforge-4pass/pineforge-corpus)
`validation/` at `442d497`, Apache-2.0: the engine's corpus gitlink when the
population was drawn; engine v1.0.0 pins `b40aa8e`, where the 100
`strategy.pine` and `tv_trades.csv` are unchanged), drawn by the engine's
`benchmarks/select_population.py` (seed 20260921; manifest in the engine's
`benchmarks/results/selection.md`). Engine v1.0.0 pins this repository at
`5759bf2`.

Each slot ships `strategy.pine`, `generated.cpp`, `strategy_pyne.py` (PyneSys
PyneComp v6.0.68), `tv_trades.csv`, and the engine outputs that the engine's
`benchmarks/run_all.sh` regenerates: `pineforge_trades.csv` and
`pynecore_trades.csv` (PyneCore 6.10.3). Every `generated.cpp` is byte-identical
to what `pineforge-codegen` 1.0.0 emits for its `strategy.pine`.
`pineforge_trades.csv` was produced by engine `35db01c8`, seven commits before
v1.0.0; engine v1.0.0 reproduces all 100 byte for byte (checked on Linux arm64,
2026-09-30). 38 slots carry an
`inputs.json`: the 36 whose corpus probe declares one, plus `028` and `029`.
Those two scripts omit `initial_capital`, for which codegen 1.0.0 declares
TradingView's newer default of 100,000, so their `inputs.json` pins the
1,000,000 their tapes were recorded with. 14 slots also carry a
`strategy_vbt.py` vectorbt port; 13 of them load and ship their
`vectorbt_trades.csv` (slot 061's port imports a `speed.vbt_helpers` module
that was never committed). `_indicators/` holds the canonical 10-indicator
script and each engine's output for it (PineForge, PyneCore, PineTS).

To reproduce, follow "Reproduce" in the engine's
[`benchmarks/README.md`](https://github.com/pineforge-4pass/pineforge-engine/blob/main/benchmarks/README.md#reproduce).

See `LEGAL.md` before redistributing any contents.
