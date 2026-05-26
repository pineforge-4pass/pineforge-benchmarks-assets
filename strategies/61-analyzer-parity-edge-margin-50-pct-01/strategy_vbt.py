import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    # Convert timestamp (ms) to DatetimeIndex in UTC
    ts_dt = pd.to_datetime(df['timestamp'], unit='ms', utc=True)

    # Monday is 0 in pandas, midnight is 00:00
    fire_signal = (ts_dt.dt.dayofweek == 0) & (ts_dt.dt.hour == 0) & (ts_dt.dt.minute == 0)
    fire_signal_v = fire_signal.values

    open_p = df['open'].values
    close_p = df['close'].values
    n = len(df)

    @njit
    def run_loop(open_p, close_p, fire_signal_v, fees):
        entries = np.zeros(n, dtype=np.bool_)
        exits = np.zeros(n, dtype=np.bool_)
        sizes = np.zeros(n, dtype=np.float64)

        equity = 1000000.0
        pos = 0
        qty = 0.0
        entry_price = 0.0
        entry_idx = -1

        for i in range(n):
            if pos == 1 and i == entry_idx + 2:
                exit_price = open_p[i]
                pnl = qty * (exit_price - entry_price)
                pnl -= fees * qty * (entry_price + exit_price)
                equity += pnl
                exits[i] = True
                pos = 0
                qty = 0.0
                entry_idx = -1

            if pos == 0 and i > 0 and fire_signal_v[i-1]:
                qty_dyn = np.round(equity * 0.5 / close_p[i-1] * 1000) / 1000
                if qty_dyn > 0:
                    entries[i] = True
                    sizes[i] = qty_dyn
                    pos = 1
                    qty = qty_dyn
                    entry_price = open_p[i]
                    entry_idx = i

        return entries, exits, sizes

    entries, exits, sizes = run_loop(open_p, close_p, fire_signal_v, fees)

    return vbt.Portfolio.from_signals(
        df['close'],
        entries=pd.Series(entries, index=df.index),
        exits=pd.Series(exits, index=df.index),
        price=df['open'],
        fees=fees,
        init_cash=1000000,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=pd.Series(sizes, index=df.index),
        size_type='Amount'
    )
