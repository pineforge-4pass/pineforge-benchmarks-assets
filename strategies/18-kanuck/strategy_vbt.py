import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit

@njit
def kanuck_loop_nb(close_p, sc, sc_threshold, ER_LEN, DEV_LEN):
    n = len(close_p)
    kama = np.empty(n, dtype=np.float64)
    kama[:] = np.nan
    kama[0] = close_p[0]
    for i in range(1, n):
        sc_val = sc[i]
        kama[i] = kama[i-1] + sc_val * (close_p[i] - kama[i-1])

    kama_dev = np.empty(n, dtype=np.float64)
    kama_dev[:] = np.nan
    for i in range(DEV_LEN - 1, n):
        sq_sum = 0.0
        for j in range(DEV_LEN):
            val = close_p[i - j] - kama[i - j]
            sq_sum += val * val
        kama_dev[i] = np.sqrt(sq_sum / DEV_LEN)

    abs_dist = np.zeros(n, dtype=np.float64)
    for i in range(n):
        if kama_dev[i] > 0:
            abs_dist[i] = abs(close_p[i] - kama[i]) / kama_dev[i]

    is_choppy = sc < sc_threshold

    kama_slope_raw = np.empty(n, dtype=np.float64)
    kama_slope_raw[:] = np.nan
    for i in range(1, n):
        kama_slope_raw[i] = kama[i] - kama[i-1]

    kama_slope = np.empty(n, dtype=np.float64)
    kama_slope[:] = np.nan
    alpha = 2.0 / (3.0 + 1.0)
    first_idx = -1
    for i in range(n):
        if not np.isnan(kama_slope_raw[i]):
            first_idx = i
            break
    if first_idx != -1:
        kama_slope[first_idx] = kama_slope_raw[first_idx]
        for i in range(first_idx + 1, n):
            kama_slope[i] = alpha * kama_slope_raw[i] + (1.0 - alpha) * kama_slope[i-1]

    slope_accel = np.zeros(n, dtype=np.bool_)
    for i in range(1, n):
        if not np.isnan(kama_slope[i]) and not np.isnan(kama_slope[i-1]):
            slope_accel[i] = kama_slope[i] > kama_slope[i-1]

    is_green = np.zeros(n, dtype=np.bool_)
    is_red = np.zeros(n, dtype=np.bool_)
    for i in range(1, n):
        if np.isnan(kama_slope[i]) or np.isnan(kama_slope[i-1]) or np.isnan(kama[i]):
            continue
        is_green[i] = (not is_choppy[i]) and (kama_slope[i] > 0.0) and (slope_accel[i] or slope_accel[i-1]) and (close_p[i] > kama[i])
        is_red[i] = (not is_choppy[i]) and (kama_slope[i] < 0.0) and (not slope_accel[i]) and (not slope_accel[i-1]) and (close_p[i] < kama[i])

    entries = np.zeros(n, dtype=np.bool_)
    exits = np.zeros(n, dtype=np.bool_)

    pos = 0 # 0: flat, 1: long
    for i in range(1, n):
        dev_ok_prev = (abs_dist[i-1] <= 1.5)
        green_prev = is_green[i-1]
        red_prev = is_red[i-1]

        if pos == 1:
            if red_prev:
                exits[i] = True
                pos = 0
        else:
            if green_prev and dev_ok_prev:
                entries[i] = True
                pos = 1

    return entries, exits

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close = df['close']
    open_val = df['open']

    ER_LEN = 10
    FAST_PERIOD = 2
    SLOW_PERIOD = 30
    DEV_LEN = 20

    net_move = (close - close.shift(ER_LEN)).abs()
    total_path = (close - close.shift(1)).abs().rolling(ER_LEN).sum()
    er = (net_move / total_path).fillna(0.0).values

    fast_sc = 2.0 / (FAST_PERIOD + 1)
    slow_sc = 2.0 / (SLOW_PERIOD + 1)
    sc = (er * (fast_sc - slow_sc) + slow_sc) ** 2
    sc_threshold = slow_sc * fast_sc

    entries, exits = kanuck_loop_nb(
        close.values,
        sc,
        sc_threshold,
        ER_LEN,
        DEV_LEN
    )

    return vbt.Portfolio.from_signals(
        close,
        entries=pd.Series(entries, index=df.index),
        exits=pd.Series(exits, index=df.index),
        price=open_val,
        init_cash=1000000,
        fees=fees,
        slippage=0.0,
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
