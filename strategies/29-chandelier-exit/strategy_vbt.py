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

    hh = df['high'].rolling(22).max().values
    ll = df['low'].rolling(22).min().values

    @njit
    def chandelier_loop_nb(high_p, low_p, close_p, hh, ll):
        tr = np.empty(n)
        tr[0] = high_p[0] - low_p[0]
        for i in range(1, n):
            tr[i] = max(high_p[i] - low_p[i], abs(high_p[i] - close_p[i-1]), abs(low_p[i] - close_p[i-1]))
        atr_val = np.empty(n)
        atr_val[:] = np.nan
        atr_val[21] = np.mean(tr[:22])
        for i in range(22, n):
            atr_val[i] = (1/22) * tr[i] + (1 - 1/22) * atr_val[i-1]

        chandLong = hh - atr_val * 3.0
        chandShort = ll + atr_val * 3.0

        entries = np.zeros(n, dtype=np.bool_)
        short_entries = np.zeros(n, dtype=np.bool_)
        pos = 0
        direction = 0

        for i in range(23, n):
            prev_direction = direction
            if close_p[i-1] > chandShort[i-2]:
                direction = 1
            if close_p[i-1] < chandLong[i-2]:
                direction = -1

            longCond = (direction == 1) and (prev_direction != 1)
            shortCond = (direction == -1) and (prev_direction != -1)

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

    entries, short_entries = chandelier_loop_nb(high_p, low_p, close_p, hh, ll)

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
