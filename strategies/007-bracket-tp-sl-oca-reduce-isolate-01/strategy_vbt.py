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

    # Indicator logic: Fast MA (9), Slow MA (21)
    # We can write simple moving averages in njit
    @njit
    def compute_sma(arr, length):
        out = np.empty(len(arr))
        out[:] = np.nan
        if len(arr) < length:
            return out
        sma_sum = 0.0
        for i in range(length):
            sma_sum += arr[i]
        out[length-1] = sma_sum / length
        for i in range(length, len(arr)):
            sma_sum = sma_sum - arr[i-length] + arr[i]
            out[i] = sma_sum / length
        return out

    fast = compute_sma(close_p, 9)
    slow = compute_sma(close_p, 21)

    @njit
    def logic_loop(open_p, high_p, low_p, close_p, fast, slow):
        entries = np.zeros(n, dtype=np.bool_)
        short_entries = np.zeros(n, dtype=np.bool_)
        exits = np.zeros(n, dtype=np.bool_)
        short_exits = np.zeros(n, dtype=np.bool_)
        exec_price = np.zeros(n, dtype=np.float64)

        pos = 0 # 1 for long, -1 for short, 0 for flat
        entry_px = 0.0

        # Since the strategy is on ETHUSDT, syminfo.mintick is 0.01 (so 10 ticks is 0.1 USDT).
        mintick = 0.01
        ticks = 10.0
        tick_dist = ticks * mintick

        for i in range(1, n):
            # Check crossovers on bar i-1 (executed at open of bar i)
            # Pine ta.crossover(fast, slow) -> fast[i-1] > slow[i-1] and fast[i-2] <= slow[i-2]
            go_long = False
            go_short = False
            if not (np.isnan(fast[i-1]) or np.isnan(slow[i-1]) or np.isnan(fast[i-2]) or np.isnan(slow[i-2])):
                go_long = (fast[i-1] > slow[i-1]) and (fast[i-2] <= slow[i-2])
                go_short = (fast[i-1] < slow[i-1]) and (fast[i-2] >= slow[i-2])

            is_reversal = (pos == -1 and go_long) or (pos == 1 and go_short)

            # 1. Check exits if in position
            if pos != 0 and not is_reversal:
                if pos == 1:
                    tp_px = entry_px + tick_dist
                    sl_px = entry_px - tick_dist

                    if open_p[i] <= sl_px:
                        exits[i] = True
                        exec_price[i] = open_p[i]
                        pos = 0
                    elif open_p[i] >= tp_px:
                        exits[i] = True
                        exec_price[i] = open_p[i]
                        pos = 0
                    elif low_p[i] <= sl_px:
                        exits[i] = True
                        exec_price[i] = sl_px
                        pos = 0
                    elif high_p[i] >= tp_px:
                        exits[i] = True
                        exec_price[i] = tp_px
                        pos = 0
                elif pos == -1:
                    tp_px = entry_px - tick_dist
                    sl_px = entry_px + tick_dist

                    if open_p[i] >= sl_px:
                        short_exits[i] = True
                        exec_price[i] = open_p[i]
                        pos = 0
                    elif open_p[i] <= tp_px:
                        short_exits[i] = True
                        exec_price[i] = open_p[i]
                        pos = 0
                    elif high_p[i] >= sl_px:
                        short_exits[i] = True
                        exec_price[i] = sl_px
                        pos = 0
                    elif low_p[i] <= tp_px:
                        short_exits[i] = True
                        exec_price[i] = tp_px
                        pos = 0

            # 2. Check entries / reversals
            if go_long:
                if pos == -1:
                    short_exits[i] = True
                    entries[i] = True
                    exec_price[i] = open_p[i]
                    pos = 1
                    entry_px = open_p[i]
                elif pos == 0:
                    entries[i] = True
                    exec_price[i] = open_p[i]
                    pos = 1
                    entry_px = open_p[i]
            elif go_short:
                if pos == 1:
                    exits[i] = True
                    short_entries[i] = True
                    exec_price[i] = open_p[i]
                    pos = -1
                    entry_px = open_p[i]
                elif pos == 0:
                    short_entries[i] = True
                    exec_price[i] = open_p[i]
                    pos = -1
                    entry_px = open_p[i]

        return entries, short_entries, exits, short_exits, exec_price

    entries, short_entries, exits, short_exits, exec_price = logic_loop(open_p, high_p, low_p, close_p, fast, slow)

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
        slippage=0.0,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
