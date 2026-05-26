import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    high_p = df['high'].values
    low_p = df['low'].values
    close_p = df['close'].values
    open_p = df['open'].values
    n = len(df)

    @njit
    def inside_bar_loop_nb(high_p, low_p, close_p, open_p):
        entries = np.zeros(n, dtype=np.bool_)
        short_entries = np.zeros(n, dtype=np.bool_)
        pos = 0
        for i in range(2, n):
            is_inside = (high_p[i-1] < high_p[i-2]) and (low_p[i-1] > low_p[i-2])
            longCond = is_inside and (close_p[i-1] > open_p[i-1])
            shortCond = is_inside and (close_p[i-1] < open_p[i-1])

            if pos == 1:
                if shortCond:
                    short_entries[i] = True
                    pos = -1
            elif pos == -1:
                if longCond:
                    entries[i] = True
                    pos = 1
            else:
                if longCond:
                    entries[i] = True
                    pos = 1
                elif shortCond:
                    short_entries[i] = True
                    pos = -1
        return entries, short_entries

    entries, short_entries = inside_bar_loop_nb(high_p, low_p, close_p, open_p)

    return vbt.Portfolio.from_signals(
        df['close'],
        entries=pd.Series(entries, index=df.index),
        short_entries=pd.Series(short_entries, index=df.index),
        price=df['open'],
        init_cash=1000000,
        fees=fees,
        slippage=0.0,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
