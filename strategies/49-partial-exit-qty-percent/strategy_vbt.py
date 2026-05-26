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

        # To track exact filled executions and support the partial exits
        pos_qty = 0.0
        entry_px = 0.0

        for i in range(1, n):
            # 1. First, handle any intraday exits/stops inside the current bar i
            timeout_triggered = False
            if pos_qty > 0.0 and hours[i-1] == 9 and minutes[i-1] == 15:
                exits[i] = True
                pos_qty = 0.0
                entry_px = 0.0
                timeout_triggered = True

            # If not timed out at the open, check for bracket fills during bar i:
            if pos_qty > 0.0 and not timeout_triggered:
                tp_px = entry_px * 1.003
                sl_px = entry_px * 0.994

                hit_tp = high_p[i] >= tp_px
                hit_sl = low_p[i] <= sl_px

                if hit_tp and hit_sl:
                    exits[i] = True
                    pos_qty = 0.0
                    entry_px = 0.0
                elif hit_tp:
                    if pos_qty == 2.0:
                        exits[i] = True
                        pos_qty = 1.0
                elif hit_sl:
                    exits[i] = True
                    pos_qty = 0.0
                    entry_px = 0.0

            # 2. Check for entries on bar i (executing at open of bar i+1)
            if hours[i] == 1 and minutes[i] == 15 and pos_qty == 0.0:
                entries[i+1] = True
                pos_qty = 2.0
                entry_px = open_p[i+1]

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
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
