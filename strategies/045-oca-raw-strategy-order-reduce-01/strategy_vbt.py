import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    if 'timestamp' in df.columns:
        dt = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
        hours = dt.dt.hour.values
        minutes = dt.dt.minute.values
    else:
        dt = pd.to_datetime(df.index, utc=True)
        hours = dt.hour.values
        minutes = dt.minute.values

    open_p = df['open'].values
    high_p = df['high'].values
    low_p = df['low'].values
    close_p = df['close'].values
    n = len(df)

    @njit
    def run_loop(open_p, high_p, low_p, close_p, hours, minutes):
        entries = np.zeros(n, dtype=np.bool_)
        exits = np.zeros(n, dtype=np.bool_)
        exec_price = np.zeros(n, dtype=np.float64)

        pos = 0
        entry_price = np.nan
        tp_price = np.nan
        sl_price = np.nan

        for i in range(1, n):
            # Check exit if in position
            if pos == 1:
                # 1. Timeout check (evaluated on prev bar)
                if hours[i-1] == 13 and minutes[i-1] == 15:
                    exits[i] = True
                    exec_price[i] = open_p[i]
                    pos = 0
                    entry_price = np.nan
                    tp_price = np.nan
                    sl_price = np.nan
                # 2. SL / TP stop and limit orders active during bar i
                elif not np.isnan(sl_price) and (open_p[i] <= sl_price):
                    exits[i] = True
                    exec_price[i] = open_p[i]
                    pos = 0
                    entry_price = np.nan
                    tp_price = np.nan
                    sl_price = np.nan
                elif not np.isnan(tp_price) and (open_p[i] >= tp_price):
                    exits[i] = True
                    exec_price[i] = open_p[i]
                    pos = 0
                    entry_price = np.nan
                    tp_price = np.nan
                    sl_price = np.nan
                elif not np.isnan(sl_price) and (low_p[i] <= sl_price):
                    exits[i] = True
                    exec_price[i] = sl_price
                    pos = 0
                    entry_price = np.nan
                    tp_price = np.nan
                    sl_price = np.nan
                elif not np.isnan(tp_price) and (high_p[i] >= tp_price):
                    exits[i] = True
                    exec_price[i] = tp_price
                    pos = 0
                    entry_price = np.nan
                    tp_price = np.nan
                    sl_price = np.nan

            # Check entry
            if pos == 0:
                if hours[i-1] == 7 and minutes[i-1] == 15:
                    entries[i] = True
                    exec_price[i] = open_p[i]
                    pos = 1
                    entry_price = open_p[i]
                    tp_price = entry_price * 1.004
                    sl_price = entry_price * 0.996

        return entries, exits, exec_price

    entries, exits, exec_price = run_loop(open_p, high_p, low_p, close_p, hours, minutes)

    price_series = pd.Series(exec_price, index=df.index)
    price_series = price_series.where(price_series > 0, df['open'])

    return vbt.Portfolio.from_signals(
        df['close'],
        entries=pd.Series(entries, index=df.index),
        exits=pd.Series(exits, index=df.index),
        price=price_series,
        fees=fees,
        init_cash=1000000,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
