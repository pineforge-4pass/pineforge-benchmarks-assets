import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close = df['close']
    open_val = df['open']
    high = df['high']
    low = df['low']

    fast = close.ewm(span=8, adjust=False).mean()
    slow = close.ewm(span=21, adjust=False).mean()

    open_p = open_val.values
    high_p = high.values
    low_p = low.values
    close_p = close.values
    fast_v = fast.fillna(0.0).values
    slow_v = slow.fillna(0.0).values
    n = len(df)

    @njit
    def run_loop(open_p, high_p, low_p, close_p, fast_v, slow_v):
        entries = np.zeros(n, dtype=np.bool_)
        short_entries = np.zeros(n, dtype=np.bool_)
        exits = np.zeros(n, dtype=np.bool_)
        short_exits = np.zeros(n, dtype=np.bool_)
        price = np.zeros(n)

        pos = 0

        for i in range(2, n):
            # 1. Close existing positions if trend flipped
            if pos == 1 and fast_v[i-1] < slow_v[i-1]:
                exits[i] = True
                price[i] = open_p[i]
                pos = 0
            elif pos == -1 and fast_v[i-1] > slow_v[i-1]:
                short_exits[i] = True
                price[i] = open_p[i]
                pos = 0

            # 2. Check pending stop entry orders
            if fast_v[i-1] > slow_v[i-1]:
                stop_price = high_p[i-2]
                if pos != 1 and high_p[i] >= stop_price:
                    entries[i] = True
                    price[i] = max(open_p[i], stop_price)
                    pos = 1
            else:
                stop_price = low_p[i-2]
                if pos != -1 and low_p[i] <= stop_price:
                    short_entries[i] = True
                    price[i] = min(open_p[i], stop_price)
                    pos = -1

        return entries, short_entries, exits, short_exits, price

    entries, short_entries, exits, short_exits, price = run_loop(
        open_p, high_p, low_p, close_p, fast_v, slow_v
    )

    price_series = pd.Series(price, index=df.index)
    price_series = price_series.where(price_series > 0, open_val)

    return vbt.Portfolio.from_signals(
        close,
        entries=pd.Series(entries, index=df.index),
        short_entries=pd.Series(short_entries, index=df.index),
        exits=pd.Series(exits, index=df.index),
        short_exits=pd.Series(short_exits, index=df.index),
        price=price_series,
        fees=fees,
        init_cash=1000000,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
