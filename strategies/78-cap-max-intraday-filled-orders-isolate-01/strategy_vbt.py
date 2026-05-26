import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close_p = df['close'].values
    open_p = df['open'].values
    n = len(df)

    if 'timestamp' in df.columns:
        dt = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
    else:
        dt = pd.to_datetime(df.index, utc=True)

    days = dt.dt.date.values

    # Indicators: Fast SMA (5), Slow SMA (13)
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

    fast = compute_sma(close_p, 5)
    slow = compute_sma(close_p, 13)

    @njit
    def logic_loop(open_p, close_p, fast, slow, days):
        entries = np.zeros(n, dtype=np.bool_)
        short_entries = np.zeros(n, dtype=np.bool_)
        exits = np.zeros(n, dtype=np.bool_)
        short_exits = np.zeros(n, dtype=np.bool_)

        pos = 0 # 1 for long, -1 for short, 0 for flat
        filled_today = 0
        current_day = days[0]

        for i in range(1, n):
            # Check day rollover to reset intraday filled count
            if days[i] != current_day:
                current_day = days[i]
                filled_today = 0

            # Crossover signals on i-1
            f = fast[i-1]
            s = slow[i-1]
            f_prev = fast[i-2]
            s_prev = slow[i-2]

            if np.isnan(f) or np.isnan(s) or np.isnan(f_prev) or np.isnan(s_prev):
                continue

            go_long = (f > s) and (f_prev <= s_prev)
            go_short = (f < s) and (f_prev >= s_prev)

            # Max intraday filled orders limit = 5
            # In Pine, strategy.risk.max_intraday_filled_orders limits the number of filled orders in a single day.
            # Every buy or sell fill (entry, exit, close) increments the fill count.
            # Once filled_today >= 5, no more orders are allowed to execute today.

            if go_long and pos <= 0:
                # If we have space for orders:
                # Reversing requires closing short and opening long -> 2 fills if opposite, or 1 fill if flat.
                needed_fills = 2 if pos == -1 else 1
                if filled_today + needed_fills <= 5:
                    if pos == -1:
                        short_exits[i] = True
                    entries[i] = True
                    pos = 1
                    filled_today += needed_fills
            elif go_short and pos >= 0:
                needed_fills = 2 if pos == 1 else 1
                if filled_today + needed_fills <= 5:
                    if pos == 1:
                        exits[i] = True
                    short_entries[i] = True
                    pos = -1
                    filled_today += needed_fills

        return entries, short_entries, exits, short_exits

    # Let's do a fast map of the date to strings/ints so we can njit compare them:
    # Converting dates to ints (YYYYMMDD) is extremely fast and works perfectly inside njit.
    date_ints = (dt.dt.year * 10000 + dt.dt.month * 100 + dt.dt.day).values

    entries, short_entries, exits, short_exits = logic_loop(open_p, close_p, fast, slow, date_ints)

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
