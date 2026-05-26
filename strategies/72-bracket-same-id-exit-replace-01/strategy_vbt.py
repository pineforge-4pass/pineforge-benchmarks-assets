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

        pos = 0 # 1 for long, 0 for flat
        entry_px = 0.0

        for i in range(1, n):
            # Timeout check on bar i-1 (executes at open of bar i)
            if pos == 1 and hours[i-1] == 16 and minutes[i-1] == 15:
                exits[i] = True
                pos = 0
                entry_px = 0.0
                continue

            # Check bracket stop/limit fills during bar i
            if pos == 1:
                # The replacement exit:
                # limit = entry * 1.003, stop = entry * 0.997
                tp_px = entry_px * 1.003
                sl_px = entry_px * 0.997

                hit_tp = high_p[i] >= tp_px
                hit_sl = low_p[i] <= sl_px

                if hit_tp or hit_sl:
                    exits[i] = True
                    pos = 0
                    entry_px = 0.0

            # Entry check on bar i (executes at open of bar i+1)
            if hours[i] == 8 and minutes[i] == 15 and pos == 0:
                entries[i+1] = True
                pos = 1
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
        slippage=0.0,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
