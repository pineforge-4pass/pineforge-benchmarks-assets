import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit
from speed.vbt_helpers import atr

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
def logic_loop(open_p, high_p, low_p, close_p, ph, pl, atr_val, atrMult, tpMult):
    n = len(close_p)
    entries = np.zeros(n, dtype=np.bool_)
    short_entries = np.zeros(n, dtype=np.bool_)
    exits = np.zeros(n, dtype=np.bool_)
    short_exits = np.zeros(n, dtype=np.bool_)
    exec_price = np.zeros(n, dtype=np.float64)

    lastPvtH = np.nan
    lastPvtL = np.nan

    pos = 0 # 0: flat, 1: long, -1: short
    stop_price = np.nan
    take_price = np.nan

    for i in range(2, n):
        # Update last pivot levels on the previous bar
        if not np.isnan(ph[i-1]):
            lastPvtH = ph[i-1]
        if not np.isnan(pl[i-1]):
            lastPvtL = pl[i-1]

        # Evaluate exit conditions for existing positions on the current bar
        if pos == 1:
            is_exit = False
            exit_px = 0.0

            if low_p[i] <= stop_price:
                is_exit = True
                exit_px = min(open_p[i], stop_price)
            elif high_p[i] >= take_price:
                is_exit = True
                exit_px = max(open_p[i], take_price)

            if is_exit:
                exits[i] = True
                exec_price[i] = exit_px
                pos = 0

        elif pos == -1:
            is_exit = False
            exit_px = 0.0

            if high_p[i] >= stop_price:
                is_exit = True
                exit_px = max(open_p[i], stop_price)
            elif low_p[i] <= take_price:
                is_exit = True
                exit_px = min(open_p[i], take_price)

            if is_exit:
                short_exits[i] = True
                exec_price[i] = exit_px
                pos = 0

        # Evaluate entry conditions on the previous bar (i-1)
        longCond = (not np.isnan(lastPvtH)) and (close_p[i-1] > lastPvtH) and (close_p[i-2] <= lastPvtH)
        shortCond = (not np.isnan(lastPvtL)) and (close_p[i-1] < lastPvtL) and (close_p[i-2] >= lastPvtL)

        # Check for reversals or new entries
        if longCond:
            if pos == -1:
                short_exits[i] = True
                if exec_price[i] == 0.0:
                    exec_price[i] = open_p[i]
                pos = 0

            if pos == 0:
                entries[i] = True
                if exec_price[i] == 0.0:
                    exec_price[i] = open_p[i]
                pos = 1
                stop_price = close_p[i-1] - atr_val[i-1] * atrMult
                take_price = close_p[i-1] + atr_val[i-1] * tpMult

        elif shortCond:
            if pos == 1:
                exits[i] = True
                if exec_price[i] == 0.0:
                    exec_price[i] = open_p[i]
                pos = 0

            if pos == 0:
                short_entries[i] = True
                if exec_price[i] == 0.0:
                    exec_price[i] = open_p[i]
                pos = -1
                stop_price = close_p[i-1] + atr_val[i-1] * atrMult
                take_price = close_p[i-1] - atr_val[i-1] * tpMult

    return entries, short_entries, exits, short_exits, exec_price

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    open_p = df['open'].values
    high_p = df['high'].values
    low_p = df['low'].values
    close_p = df['close'].values

    # Parameters from strategy.pine
    pivotLen = 5
    atrLen = 14
    atrMult = 1.5
    tpMult = 2.0

    ph = pivothigh_nb(high_p, pivotLen, pivotLen)
    pl = pivotlow_nb(low_p, pivotLen, pivotLen)
    atr_val = atr(df['high'], df['low'], df['close'], atrLen).fillna(0).values

    entries, short_entries, exits, short_exits, exec_price = logic_loop(
        open_p, high_p, low_p, close_p, ph, pl, atr_val, atrMult, tpMult
    )

    price_series = pd.Series(exec_price, index=df.index)
    price_series = price_series.where(price_series > 0, df['open'])

    return vbt.Portfolio.from_signals(
        df['close'],
        entries=pd.Series(entries, index=df.index),
        short_entries=pd.Series(short_entries, index=df.index),
        exits=pd.Series(exits, index=df.index),
        short_exits=pd.Series(short_exits, index=df.index),
        price=price_series,
        init_cash=1000000,
        fees=fees,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
