# PineForge Benchmark Assets

Private benchmark fixtures for the PineForge engine.

This repository is mounted into the public engine checkout at
`benchmarks/assets` and intentionally keeps TradingView-linked validation data
out of the public repository.

## Layout

```text
data/
  ETHUSDT_15.csv
strategies/
  001-analyzer-anvil-percent-costs-01/
  ...
  100-vwap-bands-mean-reversion-2sigma-01/
  _indicators/
```

The 100 slots are probes of the public PineForge corpus (`corpus/validation/`
at engine gitlink `442d497`, Apache-2.0), drawn by the engine's
`benchmarks/select_population.py` (seed 20260921; manifest in the engine's
`benchmarks/results/selection.md`). Each slot ships `strategy.pine`,
`generated.cpp` (codegen `89645d6`), `strategy_pyne.py` (PyneSys PyneComp
v6.0.68), `tv_trades.csv`, `inputs.json` where the probe declares one, and the
engine outputs `run_all.sh` regenerates: `pineforge_trades.csv` (engine `main`
`e9ad37dd`) and `pynecore_trades.csv` (PyneCore 6.10.2). 14 slots also carry a
`strategy_vbt.py` vectorbt port; 13 of them load and ship their
`vectorbt_trades.csv` (slot 061's port imports a `speed.vbt_helpers` module
that was never committed). `_indicators/` holds the canonical 10-indicator
script and each engine's output for it.

See `LEGAL.md` before redistributing any contents.
