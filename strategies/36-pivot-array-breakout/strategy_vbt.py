import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit

@njit
def pivothigh_nb(high: np.ndarray, left_bars: int, right_bars: int) -> np.ndarray:
    n = len(high)
    out = np.empty(n, dtype=np.float64)
    out[:] = np.nan
    total = left_bars + right_bars + 1
    for idx in range(n):
        if idx < total - 1:
            continue
        pivot = high[idx - right_bars]
        if np.isnan(pivot):
            continue

        ok = True
        for i in range(left_bars):
            val = high[idx - right_bars - left_bars + i]
            if np.isnan(val) or val > pivot:
                ok = False
                break
        if not ok:
            continue

        for i in range(right_bars):
            val = high[idx - right_bars + 1 + i]
            if np.isnan(val) or val >= pivot:
                ok = False
                break
        if ok:
            out[idx] = pivot
    return out

@njit
def pivotlow_nb(low: np.ndarray, left_bars: int, right_bars: int) -> np.ndarray:
    n = len(low)
    out = np.empty(n, dtype=np.float64)
    out[:] = np.nan
    total = left_bars + right_bars + 1
    for idx in range(n):
        if idx < total - 1:
            continue
        pivot = low[idx - right_bars]
        if np.isnan(pivot):
            continue

        ok = True
        for i in range(left_bars):
            val = low[idx - right_bars - left_bars + i]
            if np.isnan(val) or val < pivot:
                ok = False
                break
        if not ok:
            continue

        for i in range(right_bars):
            val = low[idx - right_bars + 1 + i]
            if np.isnan(val) or val <= pivot:
                ok = False
                break
        if ok:
            out[idx] = pivot
    return out

@njit
def breakout_loop_nb(close_p, p_high, p_low):
    n = len(close_p)
    entries = np.zeros(n, dtype=np.bool_)
    short_entries = np.zeros(n, dtype=np.bool_)
    exits = np.zeros(n, dtype=np.bool_)
    short_exits = np.zeros(n, dtype=np.bool_)

    # Forward fill keyRes and keySup manually
    keyRes = np.empty(n, dtype=np.float64)
    keyRes[:] = np.nan
    keySup = np.empty(n, dtype=np.float64)
    keySup[:] = np.nan

    current_res = np.nan
    current_sup = np.nan

    for i in range(n):
        if not np.isnan(p_high[i]):
            current_res = p_high[i]
        if not np.isnan(p_low[i]):
            current_sup = p_low[i]
        keyRes[i] = current_res
        keySup[i] = current_sup

    pos = 0 # 0: flat, 1: long, -1: short
    for i in range(2, n):
        keyRes_prev = keyRes[i-1]
        keySup_prev = keySup[i-1]
        close_prev = close_p[i-1]
        close_prev2 = close_p[i-2]

        longCond = (not np.isnan(keyRes_prev)) and (close_prev > keyRes_prev) and (close_prev2 <= keyRes_prev)
        shortCond = (not np.isnan(keySup_prev)) and (close_prev < keySup_prev) and (close_prev2 >= keySup_prev)

        if pos == 1:
            if shortCond:
                exits[i] = True
                short_entries[i] = True
                pos = -1
            elif (not np.isnan(keySup_prev)) and (close_prev < keySup_prev):
                exits[i] = True
                pos = 0
        elif pos == -1:
            if longCond:
                short_exits[i] = True
                entries[i] = True
                pos = 1
            elif (not np.isnan(keyRes_prev)) and (close_prev > keyRes_prev):
                short_exits[i] = True
                pos = 0
        else: # pos == 0
            if longCond:
                entries[i] = True
                pos = 1
            elif shortCond:
                short_entries[i] = True
                pos = -1

    return entries, short_entries, exits, short_exits

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    high = df['high']
    low = df['low']
    close = df['close']
    open_val = df['open']

    p_high = pivothigh_nb(high.values, 5, 5)
    p_low = pivotlow_nb(low.values, 5, 5)

    entries, short_entries, exits, short_exits = breakout_loop_nb(
        close.values,
        p_high,
        p_low
    )

    return vbt.Portfolio.from_signals(
        close,
        entries=pd.Series(entries, index=df.index),
        short_entries=pd.Series(short_entries, index=df.index),
        exits=pd.Series(exits, index=df.index),
        short_exits=pd.Series(short_exits, index=df.index),
        price=open_val,
        init_cash=1000000,
        fees=fees,
        slippage=0.0,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
