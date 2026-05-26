import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close_p = df['close'].values
    open_p = df['open'].values
    n = len(df)

    # Fast EMA (5), Slow EMA (13)
    @njit
    def compute_ema(arr, length):
        out = np.empty(len(arr))
        out[:] = np.nan
        if len(arr) < length:
            return out
        sma_init = 0.0
        for i in range(length):
            sma_init += arr[i]
        sma_init /= length
        out[length-1] = sma_init
        alpha = 2.0 / (length + 1)
        for i in range(length, len(arr)):
            out[i] = alpha * arr[i] + (1 - alpha) * out[i-1]
        return out

    ema_fast = compute_ema(close_p, 5)
    ema_slow = compute_ema(close_p, 13)

    @njit
    def logic_loop(open_p, close_p, ema_fast, ema_slow):
        entries = np.zeros(n, dtype=np.bool_)
        short_entries = np.zeros(n, dtype=np.bool_)
        exits = np.zeros(n, dtype=np.bool_)
        short_exits = np.zeros(n, dtype=np.bool_)

        pos = 0 # 1 for long, -1 for short, 0 for flat

        for i in range(1, n):
            f = ema_fast[i-1]
            s = ema_slow[i-1]
            f_prev = ema_fast[i-2]
            s_prev = ema_slow[i-2]

            if np.isnan(f) or np.isnan(s) or np.isnan(f_prev) or np.isnan(s_prev):
                continue

            long_signal = (f > s) and (f_prev <= s_prev)
            short_signal = (f < s) and (f_prev >= s_prev)

            if long_signal:
                if pos == -1:
                    short_exits[i] = True
                entries[i] = True
                pos = 1
            elif short_signal:
                if pos == 1:
                    exits[i] = True
                short_entries[i] = True
                pos = -1

        return entries, short_entries, exits, short_exits

    entries, short_entries, exits, short_exits = logic_loop(open_p, close_p, ema_fast, ema_slow)

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
