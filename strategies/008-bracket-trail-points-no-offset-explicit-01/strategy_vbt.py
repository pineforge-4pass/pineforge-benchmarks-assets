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

    if 'timestamp' in df.columns:
        dt = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
    else:
        dt = pd.to_datetime(df.index, utc=True)

    hours = dt.dt.hour.values
    minutes = dt.dt.minute.values

    @njit
    def logic_loop(open_p, high_p, low_p, close_p, hours, minutes):
        entries = np.zeros(n, dtype=np.bool_)
        short_entries = np.zeros(n, dtype=np.bool_)
        exits = np.zeros(n, dtype=np.bool_)
        short_exits = np.zeros(n, dtype=np.bool_)

        pos = 0 # 1 for long, -1 for short, 0 for flat
        entry_px = 0.0
        trail_stop = 0.0

        for i in range(1, n):
            # Check for exits during bar i
            if pos == 1:
                # LX has far stop close * 0.95 and limit close * 1.05 at entry, plus trail_points=8.
                # Since tick size for ETH is 0.01, trail_points=8 is 0.08 USDT.
                # In Pine, trail_points=8 means once the price moves in our favor by 8 points (0.08 USDT),
                # the trailing stop is activated and trailed.
                # Let's say:
                # Activation level = entry_px + 0.08.
                # If high_p[i] >= Activation level, the trailing stop is active.
                # The trailing stop price is trailing behind the highest price reached by 0.08.
                # Since we don't have trail_offset, stop level is trailed at highest_high - 0.08.
                # Let's track the maximum high reached since entry.
                # If low_p[i] <= trail_stop, we get stopped out.
                # Let's also check far stop/limit:
                hard_stop = entry_px * 0.95
                hard_limit = entry_px * 1.05

                # Trail stop activation and trailing logic:
                highest_since_entry = max(high_p[i], entry_px) # approximation or actual track
                # If we activate trailing stop:
                if high_p[i] >= entry_px + 0.08:
                    # Trailing stop price
                    trail_stop = max(trail_stop, high_p[i] - 0.08)

                if (low_p[i] <= hard_stop) or (high_p[i] >= hard_limit):
                    exits[i] = True
                    pos = 0
                elif trail_stop > 0.0 and low_p[i] <= trail_stop:
                    exits[i] = True
                    pos = 0

            elif pos == -1:
                # SX has stop close * 1.05 and limit close * 0.95, trail_points=8.
                hard_stop = entry_px * 1.05
                hard_limit = entry_px * 0.95

                if low_p[i] <= entry_px - 0.08:
                    trail_stop = min(trail_stop, low_p[i] + 0.08) if trail_stop > 0.0 else low_p[i] + 0.08

                if (high_p[i] >= hard_stop) or (low_p[i] <= hard_limit):
                    short_exits[i] = True
                    pos = 0
                elif trail_stop > 0.0 and high_p[i] >= trail_stop:
                    short_exits[i] = True
                    pos = 0

            # Entries on bar i (executed at open of bar i+1)
            is_long_time = (hours[i] == 8) and (minutes[i] == 0)
            is_short_time = (hours[i] == 20) and (minutes[i] == 0)

            if is_long_time and pos == 0:
                entries[i+1] = True
                pos = 1
                entry_px = open_p[i+1]
                trail_stop = 0.0 # reset trailing stop
            elif is_short_time and pos == 0:
                short_entries[i+1] = True
                pos = -1
                entry_px = open_p[i+1]
                trail_stop = 0.0 # reset trailing stop

        return entries, short_entries, exits, short_exits

    entries, short_entries, exits, short_exits = logic_loop(open_p, high_p, low_p, close_p, hours, minutes)

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
