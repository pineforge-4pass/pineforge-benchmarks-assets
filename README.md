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
population was drawn; engine `main` now pins `b40aa8e`, where the 100
`strategy.pine` and `tv_trades.csv` are unchanged), drawn by the engine's
`benchmarks/select_population.py` (seed 20260921; manifest in the engine's
`benchmarks/results/selection.md`). Each slot ships `strategy.pine`,
`generated.cpp` (codegen `89645d6`, 11 commits after v0.10.4 on codegen-oss
`main`; not in a release), `strategy_pyne.py` (PyneSys PyneComp v6.0.68),
`tv_trades.csv`, `inputs.json` where the probe declares one (36 slots), and the
engine outputs that the engine's `benchmarks/run_all.sh` regenerates:
`pineforge_trades.csv` (engine `e9ad37dd`, 436 commits after v0.13.1 on engine
`main`; not in a release) and `pynecore_trades.csv` (PyneCore 6.10.2). 14 slots
also carry a `strategy_vbt.py` vectorbt port; 13 of them load and ship their
`vectorbt_trades.csv` (slot 061's port imports a `speed.vbt_helpers` module
that was never committed). `_indicators/` holds the canonical 10-indicator
script and each engine's output for it (PineForge, PyneCore, PineTS).

To reproduce, follow "Reproduce" in the engine's
[`benchmarks/README.md`](https://github.com/pineforge-4pass/pineforge-engine/blob/main/benchmarks/README.md#reproduce).

See `LEGAL.md` before redistributing any contents.
