import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit

@njit
def range_filter_nb(close_p, smooth_rng):
    n = len(close_p)
    range_filter = np.empty(n, dtype=np.float64)
    filter_dir = np.empty(n, dtype=np.int32)

    # Initialize first bar
    range_filter[0] = close_p[0]
    filter_dir[0] = 0

    for i in range(1, n):
        c = close_p[i]
        sr = smooth_rng[i]
        prev_rf = range_filter[i-1]
        prev_fd = filter_dir[i-1]

        hi_target = prev_rf + sr
        lo_target = prev_rf - sr

        if c > hi_target:
            range_filter[i] = c - sr
            filter_dir[i] = 1
        elif c < lo_target:
            range_filter[i] = c + sr
            filter_dir[i] = -1
        else:
            filter_dir[i] = prev_fd
            if prev_fd == 1:
                new_filter = c - sr
                range_filter[i] = max(prev_rf, new_filter)
            elif prev_fd == -1:
                new_filter = c + sr
                range_filter[i] = min(prev_rf, new_filter)
            else:
                range_filter[i] = prev_rf

    return range_filter, filter_dir

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    high = df['high']
    low = df['low']
    close = df['close']
    open_val = df['open']

    filterLen = 50
    filterMult = 2.5

    hl_diff = high - low
    avgRange = hl_diff.ewm(span=filterLen, adjust=False).mean()
    smoothRng = (avgRange * filterMult).fillna(0.0).values

    _, filter_dir = range_filter_nb(close.values, smoothRng)

    # We shift filter_dir by 1 to get filterDir[1]
    filter_dir_ser = pd.Series(filter_dir, index=df.index)
    prev_filter_dir = filter_dir_ser.shift(1)

    long_cond = (filter_dir_ser == 1) & (prev_filter_dir != 1)
    short_cond = (filter_dir_ser == -1) & (prev_filter_dir != -1)

    entries = long_cond.shift(1).fillna(False)
    short_entries = short_cond.shift(1).fillna(False)

    return vbt.Portfolio.from_signals(
        close,
        entries=entries,
        short_entries=short_entries,
        price=open_val,
        init_cash=1000000,
        fees=fees,
        slippage=0.0,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
