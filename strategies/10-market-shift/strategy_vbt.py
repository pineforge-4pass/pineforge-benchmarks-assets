import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit
from speed.vbt_helpers import hma

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close = df['close'].values
    high = df['high'].values
    low = df['low'].values
    open_val = df['open'].values
    n = len(df)

    # Time-related arrays (hour, minute)
    # Using pandas DatetimeIndex to extract hour and minute
    if 'timestamp' in df.columns:
        dt = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
        hours = dt.dt.hour.values
        minutes = dt.dt.minute.values
    else:
        dt = pd.to_datetime(df.index, utc=True)
        hours = dt.hour.values
        minutes = dt.minute.values

    # Indicator calculations
    # hma1 = ta.hma(close, length)
    length = 55
    hma1 = hma(df['close'], length).fillna(0.0).values

    # hma2 = hma1[5] -> hma1 shifted by 5
    hma2 = np.roll(hma1, 5)
    hma2[:5] = 0.0 # Clear rolled values

    # level:
    # if ta.crossover(hma1, hma2): level := low
    # if ta.crossunder(hma1, hma2): level := high
    # persistent level is NA at first.
    # SMA 152
    sma152 = df['close'].rolling(152).mean().fillna(0.0).values

    @njit
    def run_market_shift_signals(close, high, low, open_val, hma1, hma2, sma152, hours, minutes):
        level = np.empty(n, dtype=np.float64)
        level[:] = np.nan

        is_red_bar = np.zeros(n, dtype=np.bool_)
        is_green_bar = np.zeros(n, dtype=np.bool_)
        is_below_sma = np.zeros(n, dtype=np.bool_)
        is_above_sma = np.zeros(n, dtype=np.bool_)

        current_level = np.nan

        # First, calculate level
        for i in range(1, n):
            # Crossover hma1 and hma2
            co = (hma1[i] > hma2[i]) and (hma1[i-1] <= hma2[i-1])
            cu = (hma1[i] < hma2[i]) and (hma1[i-1] >= hma2[i-1])

            if co:
                current_level = low[i]
            elif cu:
                current_level = high[i]

            level[i] = current_level

            if not np.isnan(current_level):
                is_red_bar[i] = close[i] < current_level
                is_green_bar[i] = not is_red_bar[i]

                is_below_sma[i] = close[i] < sma152[i]
                is_above_sma[i] = not is_below_sma[i]

        entries = np.zeros(n, dtype=np.bool_)
        short_entries = np.zeros(n, dtype=np.bool_)
        exits = np.zeros(n, dtype=np.bool_)
        short_exits = np.zeros(n, dtype=np.bool_)

        pos = 0
        entry_price = 0.0

        for i in range(3, n):
            # Time-based exit check (Daily close at specified time)
            # is_close_time = (hour == close_hour and minute >= close_minute)
            is_close_time = (hours[i] == 4 and minutes[i] >= 55)

            # Pine has process_orders_on_close = false, so conditions on bar i-1 execute on bar i open.
            is_close_time_prev = (hours[i-1] == 4 and minutes[i-1] >= 55)

            # Conditions evaluated on bar i-1
            red_prev = is_red_bar[i-1]
            green_prev = is_green_bar[i-1]
            below_sma_prev = is_below_sma[i-1]
            above_sma_prev = is_above_sma[i-1]
            close_prev = close[i-1]
            sma_prev = sma152[i-1]

            green_prev1 = is_green_bar[i-2]
            green_prev2 = is_green_bar[i-3]
            red_prev1 = is_red_bar[i-2]
            red_prev2 = is_red_bar[i-3]
            close_prev1 = close[i-2]
            sma_prev1 = sma152[i-2]

            # Long entry condition
            long_entry = green_prev and above_sma_prev
            # Short entry condition
            short_entry = red_prev and below_sma_prev

            # Exits checked on bar i-1 for execution at bar i open:
            if pos == 1:
                # 1. Close time exit
                if is_close_time_prev:
                    exits[i] = True
                    pos = 0
                # 2. Long exit conditions
                elif red_prev and (close_prev < entry_price):
                    exits[i] = True
                    pos = 0
                elif red_prev and below_sma_prev:
                    exits[i] = True
                    pos = 0
                elif green_prev1 and green_prev2 and (close_prev1 < sma_prev1) and red_prev:
                    exits[i] = True
                    pos = 0

            elif pos == -1:
                # 1. Close time exit
                if is_close_time_prev:
                    short_exits[i] = True
                    pos = 0
                # 2. Short exit conditions
                elif green_prev and (close_prev > entry_price):
                    short_exits[i] = True
                    pos = 0
                elif green_prev and above_sma_prev:
                    short_exits[i] = True
                    pos = 0
                elif red_prev1 and red_prev2 and (close_prev1 > sma_prev1) and green_prev:
                    short_exits[i] = True
                    pos = 0

            # Entry execution
            if pos == 0:
                if long_entry:
                    entries[i] = True
                    pos = 1
                    entry_price = open_val[i]
                elif short_entry:
                    short_entries[i] = True
                    pos = -1
                    entry_price = open_val[i]
            elif pos == 1:
                # If we were long and want to short
                if short_entry:
                    short_entries[i] = True
                    pos = -1
                    entry_price = open_val[i]
            elif pos == -1:
                # If we were short and want to long
                if long_entry:
                    entries[i] = True
                    pos = 1
                    entry_price = open_val[i]

        return entries, short_entries, exits, short_exits

    entries, short_entries, exits, short_exits = run_market_shift_signals(
        close, high, low, open_val, hma1, hma2, sma152, hours, minutes
    )

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
