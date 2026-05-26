import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit
from speed.vbt_helpers import rsi

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close = df['close']
    rsi_val = rsi(close, 14)
    entry_cond = (rsi_val > 50.0) & (rsi_val.shift(1) <= 50.0)
    exit_cond = (rsi_val < 50.0) & (rsi_val.shift(1) >= 50.0)

    open_p = df['open'].values
    high_p = df['high'].values
    low_p = df['low'].values
    close_p = df['close'].values
    entry_v = entry_cond.fillna(False).values
    exit_v = exit_cond.fillna(False).values
    n = len(df)

    @njit
    def run_loop(open_p, high_p, low_p, close_p, entry_v, exit_v):
        entries = np.zeros(n, dtype=np.bool_)
        exits = np.zeros(n, dtype=np.bool_)

        pos = 0
        stop_lvl = np.nan

        for i in range(1, n):
            # Check exit from previous bar's exit condition
            if pos == 1:
                if exit_v[i-1]:
                    exits[i] = True
                    pos = 0
                    stop_lvl = np.nan
                elif not np.isnan(stop_lvl) and (low_p[i] <= stop_lvl):
                    exits[i] = True
                    pos = 0
                    stop_lvl = np.nan

            # Check entry
            if pos == 0:
                if entry_v[i-1]:
                    entries[i] = True
                    pos = 1
                    stop_lvl = (open_p[i-1] + high_p[i-1]) * 0.5
                    # Same bar stop-loss check
                    if low_p[i] <= stop_lvl:
                        exits[i] = True
                        pos = 0
                        stop_lvl = np.nan

        return entries, exits

    entries, exits = run_loop(open_p, high_p, low_p, close_p, entry_v, exit_v)

    return vbt.Portfolio.from_signals(
        close,
        entries=pd.Series(entries, index=df.index),
        exits=pd.Series(exits, index=df.index),
        price=open_p,
        fees=fees,
        init_cash=1000000,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
