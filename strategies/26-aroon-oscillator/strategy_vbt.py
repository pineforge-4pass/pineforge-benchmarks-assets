import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit

@njit
def aroon_loop(high_p: np.ndarray, low_p: np.ndarray, close_p: np.ndarray, ma_val: np.ndarray, hh: np.ndarray, ll: np.ndarray):
    n = len(close_p)
    entries = np.zeros(n, dtype=np.bool_)
    short_entries = np.zeros(n, dtype=np.bool_)
    exits = np.zeros(n, dtype=np.bool_)
    short_exits = np.zeros(n, dtype=np.bool_)

    newHigh_arr = np.zeros(n, dtype=np.bool_)
    last_max = np.nan
    last_max_index = 0
    for idx in range(n):
        val = high_p[idx]
        if np.isnan(val):
            newHigh_arr[idx] = False
            continue
        if np.isnan(last_max) or val > last_max:
            last_max = val
            last_max_index = 0
        if last_max_index >= 20:
            last_max = val
            last_max_index = 0
            for i in range(1, 20):
                s = high_p[idx - i]
                if s > last_max:
                    last_max = s
                    last_max_index = i
                elif s == last_max:
                    last_max_index = i
        max_index = last_max_index
        last_max_index += 1
        if idx < 19:
            newHigh_arr[idx] = False
        else:
            newHigh_arr[idx] = (max_index == 0)

    newLow_arr = np.zeros(n, dtype=np.bool_)
    last_min = np.nan
    last_min_index = 0
    for idx in range(n):
        val = low_p[idx]
        if np.isnan(val):
            newLow_arr[idx] = False
            continue
        if np.isnan(last_min) or val < last_min:
            last_min = val
            last_min_index = 0
        if last_min_index >= 20:
            last_min = val
            last_min_index = 0
            for i in range(1, 20):
                s = low_p[idx - i]
                if s < last_min:
                    last_min = s
                    last_min_index = i
                elif s == last_min:
                    last_min_index = i
        min_index = last_min_index
        last_min_index += 1
        if idx < 19:
            newLow_arr[idx] = False
        else:
            newLow_arr[idx] = (min_index == 0)

    pos = 0
    for i in range(20, n):
        longCond = newHigh_arr[i-1] and (close_p[i-1] > ma_val[i-1])
        shortCond = newLow_arr[i-1] and (close_p[i-1] < ma_val[i-1])

        mid_chan = (hh[i-1] + ll[i-1]) / 2
        exitLongCond = (pos == 1) and (close_p[i-1] < mid_chan)
        exitShortCond = (pos == -1) and (close_p[i-1] > mid_chan)

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
    high_p = df['high']
    low_p = df['low']
    open_val = df['open']

    hh = high_p.rolling(20).max().values
    ll = low_p.rolling(20).min().values
    ma_val = close.ewm(span=50, adjust=False).mean().values
    ma_val[:49] = np.nan

    entries, short_entries, exits, short_exits = aroon_loop(
        high_p.values, low_p.values, close.values, ma_val, hh, ll
    )

    return vbt.Portfolio.from_signals(
        close,
        entries=pd.Series(entries, index=close.index),
        short_entries=pd.Series(short_entries, index=close.index),
        exits=pd.Series(exits, index=close.index),
        short_exits=pd.Series(short_exits, index=close.index),
        price=open_val,
        init_cash=1000000,
        fees=fees,
        slippage=0.0,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
