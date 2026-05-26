import pandas as pd
import numpy as np
import vectorbt as vbt
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
from speed.vbt_helpers import rsi

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close = df['close']
    open_val = df['open']

    dts = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
    hours = dts.dt.hour.values
    pandas_dayofweek = dts.dt.dayofweek.values
    days = (pandas_dayofweek + 1) % 7

    rsi_series = rsi(close, 14)
    rsi_val = rsi_series.values

    n = len(df)
    entries = np.zeros(n, dtype=np.bool_)
    exits = np.zeros(n, dtype=np.bool_)
    short_entries = np.zeros(n, dtype=np.bool_)
    short_exits = np.zeros(n, dtype=np.bool_)

    mask = np.zeros((24, 7), dtype=np.bool_)
    pos = 0

    for i in range(n - 1):
        rsi_i = rsi_val[i]
        h_i = hours[i]
        d_i = days[i]

        if not np.isnan(rsi_i) and rsi_i > 60.0 and 0 <= h_i < 24 and 0 <= d_i < 7:
            mask[h_i, d_i] = True

        h_idx = h_i if (0 <= h_i < 24) else 0
        d_idx = d_i if (0 <= d_i < 7) else 0
        sample = mask[h_idx, d_idx]

        hotCount = mask.sum()

        entryCond = (hotCount >= 6) and (rsi_i > 55.0) and sample
        exitCond = not np.isnan(rsi_i) and rsi_i < 45.0

        if pos == 0 and entryCond:
            entries[i+1] = True
            pos = 1
        elif pos == 1 and exitCond:
            exits[i+1] = True
            pos = 0

    return vbt.Portfolio.from_signals(
        close,
        entries=pd.Series(entries, index=df.index),
        short_entries=pd.Series(short_entries, index=df.index),
        exits=pd.Series(exits, index=df.index),
        short_exits=pd.Series(short_exits, index=df.index),
        price=open_val,
        init_cash=1000000,
        fees=fees,
        slippage=0.0,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
