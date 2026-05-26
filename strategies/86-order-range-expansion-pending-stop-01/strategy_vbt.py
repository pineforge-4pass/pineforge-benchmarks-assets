import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit
from speed.vbt_helpers import atr

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    high = df['high']
    low = df['low']
    close = df['close']
    open_val = df['open']

    i_atr_len = 14
    i_atr_mult = 1.0

    prev_range = high.shift(1) - low.shift(1)
    atr_now = atr(high, low, close, i_atr_len)
    atr_prev = atr_now.shift(1)

    expansion = atr_prev.notna() & (prev_range > atr_prev * i_atr_mult)

    prev_up = close.shift(1) > open_val.shift(1)
    prev_down = close.shift(1) < open_val.shift(1)

    arm_long = expansion & prev_up
    arm_short = expansion & prev_down

    open_p = open_val.values
    high_p = high.values
    low_p = low.values
    close_p = close.values
    arm_long_v = arm_long.fillna(False).values
    arm_short_v = arm_short.fillna(False).values
    n = len(df)

    @njit
    def run_loop(open_p, high_p, low_p, close_p, arm_long_v, arm_short_v):
        entries = np.zeros(n, dtype=np.bool_)
        short_entries = np.zeros(n, dtype=np.bool_)
        price = np.zeros(n)

        pos = 0

        for i in range(2, n):
            # Check if long order is active from previous bar and we are not long
            if arm_long_v[i-1] and pos != 1:
                stop_price = high_p[i-2]
                if high_p[i] >= stop_price:
                    entries[i] = True
                    price[i] = max(open_p[i], stop_price)
                    pos = 1
            # Check if short order is active from previous bar and we are not short
            elif arm_short_v[i-1] and pos != -1:
                stop_price = low_p[i-2]
                if low_p[i] <= stop_price:
                    short_entries[i] = True
                    price[i] = min(open_p[i], stop_price)
                    pos = -1

        return entries, short_entries, price

    entries, short_entries, price = run_loop(open_p, high_p, low_p, close_p, arm_long_v, arm_short_v)

    # For any bars where no signal was generated, set price to open (default)
    price_series = pd.Series(price, index=df.index)
    price_series = price_series.where(price_series > 0, open_val)

    return vbt.Portfolio.from_signals(
        close,
        entries=pd.Series(entries, index=df.index),
        short_entries=pd.Series(short_entries, index=df.index),
        price=price_series,
        fees=fees,
        init_cash=1000000,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
