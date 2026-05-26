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

    # i_pivot = 5
    # ta.pivothigh(high, 5, 5) and ta.pivotlow(low, 5, 5)
    # Pivot calculation: pivot occurs on bar i-5 if high[i-5] is the maximum of high[i-10 : i]
    # Let's write the pivot detector inside @njit
    @njit
    def logic_loop(open_p, high_p, low_p, close_p):
        entries = np.zeros(n, dtype=np.bool_)
        short_entries = np.zeros(n, dtype=np.bool_)
        exits = np.zeros(n, dtype=np.bool_)
        short_exits = np.zeros(n, dtype=np.bool_)

        lastSwingHigh = np.nan
        lastSwingLow = np.nan
        prevSwingHigh = np.nan
        prevSwingLow = np.nan
        structureDirection = 0

        # We need to track the bar index when the position was opened to support:
        # "bar_index > strategy.opentrades.entry_bar_index(0)"
        entry_bar = -1
        pos = 0 # 1 for long, -1 for short, 0 for flat

        for i in range(11, n):
            # 1. First, check if we need to close the position at the open of bar i:
            # "if strategy.position_size != 0 and bar_index > strategy.opentrades.entry_bar_index(0)"
            # This is evaluated on bar i-1. If true on bar i-1, we close on bar i open.
            if pos != 0 and (i - 1) > entry_bar:
                if pos == 1:
                    exits[i] = True
                else:
                    short_exits[i] = True
                pos = 0
                entry_bar = -1

            # 2. Compute pivots on bar i-1:
            # pivotHigh occurs at i-1-5 if high[i-1-5] is the max of high[i-1-10 : i-1]
            # Since i_pivot = 5, we look at the window of 11 bars from i-1-10 to i-1.
            # Center bar is i-1-5.
            p_high_idx = i - 1 - 5
            is_p_high = True
            for k in range(i - 1 - 10, i):
                if high_p[k] > high_p[p_high_idx]:
                    is_p_high = False
                    break
            pivotHigh = high_p[p_high_idx] if is_p_high else np.nan

            p_low_idx = i - 1 - 5
            is_p_low = True
            for k in range(i - 1 - 10, i):
                if low_p[k] < low_p[p_low_idx]:
                    is_p_low = False
                    break
            pivotLow = low_p[p_low_idx] if is_p_low else np.nan

            # Update swing states:
            if not np.isnan(pivotHigh):
                prevSwingHigh = lastSwingHigh
                lastSwingHigh = pivotHigh

            if not np.isnan(pivotLow):
                prevSwingLow = lastSwingLow
                lastSwingLow = pivotLow

            # Check bos/choch conditions on bar i-1:
            bosUp = (not np.isnan(lastSwingHigh)) and (close_p[i-1] > lastSwingHigh) and (structureDirection <= 0)
            bosDown = (not np.isnan(lastSwingLow)) and (close_p[i-1] < lastSwingLow) and (structureDirection >= 0)
            chochUp = (not np.isnan(prevSwingHigh)) and (close_p[i-1] > prevSwingHigh) and (structureDirection < 0)
            chochDown = (not np.isnan(prevSwingLow)) and (close_p[i-1] < prevSwingLow) and (structureDirection > 0)

            if bosUp or chochUp:
                structureDirection = 1
            if bosDown or chochDown:
                structureDirection = -1

            any_bull_event = bosUp or chochUp
            any_bear_event = bosDown or chochDown

            # If no position is active, can entry on bar i open:
            if pos == 0:
                if any_bull_event:
                    entries[i] = True
                    pos = 1
                    entry_bar = i
                elif any_bear_event:
                    short_entries[i] = True
                    pos = -1
                    entry_bar = i

        return entries, short_entries, exits, short_exits

    entries, short_entries, exits, short_exits = logic_loop(open_p, high_p, low_p, close_p)

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
