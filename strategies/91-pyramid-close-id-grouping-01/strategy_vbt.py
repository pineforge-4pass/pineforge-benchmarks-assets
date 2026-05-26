import pandas as pd
import numpy as np
import vectorbt as vbt

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    utc_time = pd.to_datetime(df['timestamp'], unit='ms').dt.tz_localize('UTC')
    h = utc_time.dt.hour.values
    m = utc_time.dt.minute.values
    n = len(df)

    entries = np.zeros(n, dtype=np.bool_)
    short_entries = np.zeros(n, dtype=np.bool_)
    exits = np.zeros(n, dtype=np.bool_)
    short_exits = np.zeros(n, dtype=np.bool_)

    pos_size = 0
    for i in range(n - 1):
        # Long entries/exits
        if h[i] == 0 and m[i] == 15 and pos_size == 0:
            entries[i+1] = True
            pos_size += 1
        elif h[i] == 0 and m[i] == 30 and pos_size > 0:
            entries[i+1] = True
            pos_size += 1
        elif h[i] == 0 and m[i] == 45 and pos_size > 0:
            entries[i+1] = True
            pos_size += 1
        elif h[i] == 1 and m[i] == 15 and pos_size > 0:
            exits[i+1] = True
            pos_size = 0

        # Short entries/exits
        elif h[i] == 12 and m[i] == 15 and pos_size == 0:
            short_entries[i+1] = True
            pos_size -= 1
        elif h[i] == 12 and m[i] == 30 and pos_size < 0:
            short_entries[i+1] = True
            pos_size -= 1
        elif h[i] == 12 and m[i] == 45 and pos_size < 0:
            short_entries[i+1] = True
            pos_size -= 1
        elif h[i] == 13 and m[i] == 15 and pos_size < 0:
            short_exits[i+1] = True
            pos_size = 0

    # Create size Series where exits specify np.inf to close all accumulated entries
    size = pd.Series(1.0, index=df.index)
    size[exits] = np.inf
    size[short_exits] = np.inf

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
        accumulate=True,
        size=size,
        size_type='Amount',
        trades_type='EntryTrades'
    )
