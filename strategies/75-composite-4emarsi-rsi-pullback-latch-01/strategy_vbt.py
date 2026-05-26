import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close_p = df['close'].values
    high_p = df['high'].values
    low_p = df['low'].values
    open_p = df['open'].values
    n = len(df)

    # 1. RSI Base with period 14.
    # We can write rsi helper inside njit or use speed.vbt_helpers if it's imported.
    # Let's write standard RSI calculation inside @njit to make it self-contained and fast.
    @njit
    def compute_rsi(arr, period=14):
        out = np.empty(len(arr))
        out[:] = np.nan
        if len(arr) < period:
            return out

        # Calculate changes
        gains = np.zeros(len(arr))
        losses = np.zeros(len(arr))
        for i in range(1, len(arr)):
            diff = arr[i] - arr[i-1]
            if diff > 0:
                gains[i] = diff
            else:
                losses[i] = -diff

        # First values are SMA of gains and losses
        sum_g = 0.0
        sum_l = 0.0
        for i in range(1, period + 1):
            sum_g += gains[i]
            sum_l += losses[i]

        avg_g = sum_g / period
        avg_l = sum_l / period

        if avg_l == 0:
            out[period] = 100.0
        else:
            rs = avg_g / avg_l
            out[period] = 100.0 - (100.0 / (1.0 + rs))

        alpha = 1.0 / period
        for i in range(period + 1, len(arr)):
            avg_g = alpha * gains[i] + (1 - alpha) * avg_g
            avg_l = alpha * losses[i] + (1 - alpha) * avg_l
            if avg_l == 0:
                out[i] = 100.0
            else:
                rs = avg_g / avg_l
                out[i] = 100.0 - (100.0 / (1.0 + rs))
        return out

    r_val = compute_rsi(close_p, 14)

    @njit
    def logic_loop(open_p, high_p, low_p, close_p, r_val):
        entries = np.zeros(n, dtype=np.bool_)
        short_entries = np.zeros(n, dtype=np.bool_)
        exits = np.zeros(n, dtype=np.bool_)
        short_exits = np.zeros(n, dtype=np.bool_)

        long_armed = False
        short_armed = False
        pos = 0 # 1 for long, -1 for short, 0 for flat

        for i in range(1, n):
            r = r_val[i-1]
            r_prev = r_val[i-2]

            if np.isnan(r) or np.isnan(r_prev):
                continue

            # Check pullback arming
            if r < 40.0:
                long_armed = True
            if r > 60.0:
                short_armed = True

            # ta.crossover(r, 50.0) -> r > 50.0 and r_prev <= 50.0
            long_fire = long_armed and (r > 50.0) and (r_prev <= 50.0)
            # ta.crossunder(r, 50.0) -> r < 50.0 and r_prev >= 50.0
            short_fire = short_armed and (r < 50.0) and (r_prev >= 50.0)

            if long_fire:
                long_armed = False
            if short_fire:
                short_armed = False

            # Order routing
            if long_fire and pos <= 0:
                if pos == -1:
                    short_exits[i] = True
                entries[i] = True
                pos = 1
            elif short_fire and pos >= 0:
                if pos == 1:
                    exits[i] = True
                short_entries[i] = True
                pos = -1

        return entries, short_entries, exits, short_exits

    entries, short_entries, exits, short_exits = logic_loop(open_p, high_p, low_p, close_p, r_val)

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
