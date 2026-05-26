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

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    high_val = df['high'].values
    low_val = df['low'].values
    close_val = df['close']
    open_val = df['open']

    ph = pivothigh_nb(high_val, 4, 2)
    pl = pivotlow_nb(low_val, 4, 2)

    entries = pd.Series(~np.isnan(pl), index=df.index).shift(1).fillna(False)
    short_entries = pd.Series(~np.isnan(ph), index=df.index).shift(1).fillna(False)

    return vbt.Portfolio.from_signals(
        close_val,
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
