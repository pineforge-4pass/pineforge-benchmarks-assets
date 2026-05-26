import pandas as pd
import numpy as np
import vectorbt as vbt
from speed.vbt_helpers import cci
from speed.vbt_helpers import ema_ribbon_transitions # dummy or use cci_momentum_loop
from numba import njit

@njit
def cci_momentum_loop(cci_val: np.ndarray, os_level: float = -100.0, ob_level: float = 100.0):
    n = len(cci_val)
    entries = np.zeros(n, dtype=np.bool_)
    short_entries = np.zeros(n, dtype=np.bool_)
    exits = np.zeros(n, dtype=np.bool_)
    short_exits = np.zeros(n, dtype=np.bool_)

    pos = 0
    crossunder_initialized = False
    crossunder_state = False
    crossover_initialized = False
    crossover_state = False

    for i in range(2, n):
        if np.isnan(cci_val[i-1]) or np.isnan(cci_val[i-2]):
            continue

        longCond = (cci_val[i-1] > os_level) and (cci_val[i-2] <= os_level)
        shortCond = (cci_val[i-1] < ob_level) and (cci_val[i-2] >= ob_level)

        exitLongCond = False
        if pos == 1:
            x = cci_val[i-1]
            if not crossunder_initialized:
                res = False
                crossunder_initialized = True
            else:
                res = (x < 0.0) and crossunder_state
            crossunder_state = (x >= 0.0)
            exitLongCond = res

        exitShortCond = False
        if pos == -1:
            x = cci_val[i-1]
            if not crossover_initialized:
                res = False
                crossover_initialized = True
            else:
                res = (x > 0.0) and crossover_state
            crossover_state = (x <= 0.0)
            exitShortCond = res

        if pos == 1:
            if shortCond:
                short_entries[i] = True
                pos = -1
            elif exitLongCond:
                exits[i] = True
                pos = 0
        elif pos == -1:
            if longCond:
                entries[i] = True
                pos = 1
            elif exitShortCond:
                short_exits[i] = True
                pos = 0
        else:
            if longCond:
                entries[i] = True
                pos = 1
            elif shortCond:
                short_entries[i] = True
                pos = -1

    return entries, short_entries, exits, short_exits

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close = df['close']
    open_val = df['open']
    cci_val = cci(close, 20).values.astype(np.float64)

    entries, short_entries, exits, short_exits = cci_momentum_loop(cci_val)

    entries = pd.Series(entries, index=close.index)
    short_entries = pd.Series(short_entries, index=close.index)
    exits = pd.Series(exits, index=close.index)
    short_exits = pd.Series(short_exits, index=close.index)

    return vbt.Portfolio.from_signals(
        close,
        entries=entries,
        short_entries=short_entries,
        exits=exits,
        short_exits=short_exits,
        price=open_val,
        init_cash=1000000,
        fees=fees,
        slippage=0.0,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
