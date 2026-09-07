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
  01-sma-cross/
  ...
  _indicators/
```

See `LEGAL.md` before redistributing any contents.

## Benchmark branch `bench/pynesys-2026-09`

Two extra trees exist only on this branch, for the PineForge vs PyneSys/PyneCore benchmark
(`pineforge-engine/benchmarks/results/pynesys-2026-09/`):

```text
corpus-pyne/<slug>/strategy_pyne.py        PyneCore sources for the public corpus (set B),
                                           compiled by PyneComp v6.0.66
suite-pyne-6.0.66/<slug>/strategy_pyne.py  the public benchmark suite (set A) RE-compiled by
                                           PyneComp v6.0.66, for the compiler-drift column
```

`strategies/<slug>/strategy_pyne.py` keeps the committed PyneComp **v6.0.31** sources the suite
has always shipped. `suite-pyne-6.0.66/` is the same 100 strategies through today's compiler, run
on the identical PyneCore 6.9.1 runtime so the compiler version is the only variable: 94 of 100
generated bodies are byte-identical, 6 differ, and exactly one tier moves. Both columns are
published in the benchmark's tables; see its `drift_setA.csv` and `drift_A.py`.
