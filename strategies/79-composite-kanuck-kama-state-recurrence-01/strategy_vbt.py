import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close_p = df['close'].values
    open_p = df['open'].values
    n = len(df)

    # Manual KAMA (Kaufman Adaptive MA) Recurrence
    # i_kama_len = 14, i_kama_fast = 2, i_kama_slow = 30
    @njit
    def compute_kama(arr, length=14, fast_len=2, slow_len=30):
        out = np.empty(len(arr))
        out[:] = np.nan
        if len(arr) < length:
            return out

        # Prepare change_n and vol_sum
        # Pine: change_n = abs(close - close[14])
        # Pine: vol_sum = sum(abs(close - close[1]), 14)
        abs_diff = np.empty(len(arr))
        abs_diff[0] = 0.0
        for i in range(1, len(arr)):
            abs_diff[i] = abs(arr[i] - arr[i-1])

        fast_sc = 2.0 / (fast_len + 1)
        slow_sc = 2.0 / (slow_len + 1)

        # Initialize kama at length-1 index with SMA or first value
        kama = arr[length-1]
        out[length-1] = kama

        for i in range(length, len(arr)):
            change_n = abs(arr[i] - arr[i - length])
            vol_sum = 0.0
            for j in range(i - length + 1, i + 1):
                vol_sum += abs_diff[j]

            er = change_n / vol_sum if vol_sum > 0.0 else 0.0
            sc = (er * (fast_sc - slow_sc) + slow_sc) ** 2

            kama = kama + sc * (arr[i] - kama)
            out[i] = kama

        return out

    kama_val = compute_kama(close_p, 14, 2, 30)

    @njit
    def logic_loop(open_p, close_p, kama_val):
        entries = np.zeros(n, dtype=np.bool_)
        short_entries = np.zeros(n, dtype=np.bool_)
        exits = np.zeros(n, dtype=np.bool_)
        short_exits = np.zeros(n, dtype=np.bool_)

        pos = 0 # 1 for long, -1 for short, 0 for flat

        for i in range(1, n):
            c = close_p[i-1]
            c_prev = close_p[i-2]
            k = kama_val[i-1]
            k_prev = kama_val[i-2]

            if np.isnan(k) or np.isnan(k_prev):
                continue

            cross_up = (c > k) and (c_prev <= k_prev)
            cross_down = (c < k) and (c_prev >= k_prev)

            if cross_up:
                if pos == -1:
                    short_exits[i] = True
                entries[i] = True
                pos = 1
            elif cross_down:
                if pos == 1:
                    exits[i] = True
                short_entries[i] = True
                pos = -1

        return entries, short_entries, exits, short_exits

    entries, short_entries, exits, short_exits = logic_loop(open_p, close_p, kama_val)

    return vbt.Portfolio.from_signals(
        df['close'],
        entries=pd.Series(entries, index=df.index),
        short_entries=pd.Series(short_entries, index=df.index),
        exits=pd.Series(exits, index=df.index),
        short_exits=pd.Series(short_exits, index=df.index),
        price=df['open'],
        init_cash=1000000,
        fees=fees,
        slippage=0.0,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
