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

    # Fast EMA (9), Slow EMA (21)
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

    ema9 = compute_ema(close_p, 9)
    ema21 = compute_ema(close_p, 21)

    @njit
    def logic_loop(open_p, high_p, low_p, close_p, ema9, ema21):
        entries = np.zeros(n, dtype=np.bool_)
        short_entries = np.zeros(n, dtype=np.bool_)
        exits = np.zeros(n, dtype=np.bool_)
        short_exits = np.zeros(n, dtype=np.bool_)

        pos = 0 # 1 for long, 0 for flat
        entry_px = 0.0

        for i in range(1, n):
            # Check crossover / crossunder conditions on bar i-1 (executed on bar i open)
            f = ema9[i-1]
            s = ema21[i-1]
            f_prev = ema9[i-2]
            s_prev = ema21[i-2]

            if np.isnan(f) or np.isnan(s) or np.isnan(f_prev) or np.isnan(s_prev):
                continue

            entryCond = (f > s) and (f_prev <= s_prev)
            exitCond = (f < s) and (f_prev >= s_prev)

            # Check exits during bar i
            # "strategy.exit('X', from_entry='L', stop=stopLvl)"
            # stopLvl is calculated on bar i-1 (when entryCond occurs)
            # Actually, "float stopLvl = (open + high) * 0.5" is calculated on bar i-1 (when entryCond occurs),
            # and applied to the exit order.
            # So if entryCond evaluates to true on bar i-1, we entry long on bar i open.
            # At the same time, we set stopLvl = (open[i-1] + high[i-1]) * 0.5.
            # And the exit order stop=stopLvl is active for bar i.
            # If low_p[i] <= stopLvl, we get stopped out on bar i.

            if pos == 1:
                # Stop price calculated when entryCond happened (at i-2)
                # Let's say entry happened at open of bar i-1 (because entryCond was true at i-2).
                # We need to compute stop level at that entry.
                # In Pine:
                # if entryCond and strategy.position_size == 0:
                #     strategy.entry("L", ...)
                #     stopLvl = (open + high) * 0.5
                # So if entryCond was true at i-2, the entry is placed at i-1 open, and stopLvl is (open[i-2] + high[i-2]) * 0.5.
                # Since we entry on bar i, we need to know what stopLvl was.
                # Let's track stop_px.
                pass

            # Exit condition check
            if exitCond and pos == 1:
                exits[i] = True
                pos = 0
                entry_px = 0.0

            # Bracket exit check
            # In Pine, "stopLvl = (open + high) * 0.5" is calculated on the bar where strategy.exit is called.
            # Since strategy.exit is called inside the `if entryCond` block, which runs on the bar of entryCond (i-1),
            # the stop price is based on that bar's open and high: `(open_p[i-1] + high_p[i-1]) * 0.5`.
            # This order is sent at i-1 close, so it's active starting from bar i.
            # If the entry fills at open_p[i], the exit is already active during bar i.
            # So we check if low_p[i] <= stopLvl.
            # Let's model this carefully:
            # We track the active stop_lvl.
            # If pos == 1:
            #     check if low_p[i] <= stop_lvl
            #     if so, exits[i] = True, pos = 0
            # Note: if both entry Cond was true on i-1, and stop level is hit on i, does it exit? Yes.
            # Let's implement this state tracking:
            active_stop_lvl = 0.0

            if pos == 1 and active_stop_lvl > 0.0:
                if low_p[i] <= active_stop_lvl:
                    exits[i] = True
                    pos = 0
                    active_stop_lvl = 0.0

            # Entries on bar i open (if entryCond was true on bar i-1)
            if entryCond and pos == 0:
                entries[i] = True
                pos = 1
                entry_px = open_p[i]
                active_stop_lvl = (open_p[i-1] + high_p[i-1]) * 0.5

        return entries, short_entries, exits, short_exits

    entries, short_entries, exits, short_exits = logic_loop(open_p, high_p, low_p, close_p, ema9, ema21)

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
