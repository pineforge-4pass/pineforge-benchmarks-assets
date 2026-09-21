import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit
from speed.vbt_helpers import rsi, atr

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    if 'timestamp' in df.columns:
        dt = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
        hours = dt.dt.hour.values
        minutes = dt.dt.minute.values
    else:
        dt = pd.to_datetime(df.index, utc=True)
        hours = dt.hour.values
        minutes = dt.minute.values

    close = df['close']
    high = df['high']
    low = df['low']

    rsi_val = rsi(close, 14)
    ema_fast = close.ewm(span=9, adjust=False).mean()
    ema_slow = close.ewm(span=21, adjust=False).mean()
    atr_val = atr(high, low, close, 14)

    long_cond = (ema_fast > ema_slow) & (ema_fast.shift(1) <= ema_slow.shift(1)) & (rsi_val < 70)
    short_stop = (rsi_val < 50) & (rsi_val.shift(1) >= 50)

    open_p = df['open'].values
    high_p = high.values
    low_p = low.values
    close_p = close.values
    atr_v = atr_val.fillna(0.0).values
    long_cond_v = long_cond.fillna(False).values
    short_stop_v = short_stop.fillna(False).values
    n = len(df)

    @njit
    def run_loop(open_p, high_p, low_p, close_p, hours, minutes, long_cond_v, short_stop_v, atr_v):
        entries = np.zeros(n, dtype=np.bool_)
        short_entries = np.zeros(n, dtype=np.bool_)
        exits = np.zeros(n, dtype=np.bool_)
        short_exits = np.zeros(n, dtype=np.bool_)
        price = np.zeros(n)

        pos = 0

        for i in range(1, n):
            # 1. close_all at open
            if hours[i-1] == 21 and minutes[i-1] == 45:
                if pos > 0:
                    exits[i] = True
                    price[i] = open_p[i]
                    pos = 0
                elif pos < 0:
                    short_exits[i] = True
                    price[i] = open_p[i]
                    pos = 0

            # 2. long market entry at open
            if long_cond_v[i-1]:
                if pos < 0:
                    entries[i] = True
                    price[i] = open_p[i]
                    pos = 1
                elif pos < 4:
                    entries[i] = True
                    price[i] = open_p[i]
                    pos += 1

            # 3. short stop entry during bar i
            if short_stop_v[i-1]:
                stop_price = low_p[i-1] - atr_v[i-1] * 0.25
                if low_p[i] <= stop_price:
                    fill_price = min(open_p[i], stop_price)
                    if pos > 0:
                        short_entries[i] = True
                        price[i] = fill_price
                        pos = -1
                    elif pos > -4:
                        short_entries[i] = True
                        price[i] = fill_price
                        pos -= 1

        return entries, short_entries, exits, short_exits, price

    entries, short_entries, exits, short_exits, price = run_loop(
        open_p, high_p, low_p, close_p, hours, minutes, long_cond_v, short_stop_v, atr_v
    )

    price_series = pd.Series(price, index=df.index)
    price_series = price_series.where(price_series > 0, df['open'])

    return vbt.Portfolio.from_signals(
        close,
        entries=pd.Series(entries, index=df.index),
        short_entries=pd.Series(short_entries, index=df.index),
        exits=pd.Series(exits, index=df.index),
        short_exits=pd.Series(short_exits, index=df.index),
        price=price_series,
        fees=fees,
        init_cash=1000000,
        upon_opposite_entry='reverse',
        accumulate=True,
        size=1.0,
        size_type='Amount'
    )
