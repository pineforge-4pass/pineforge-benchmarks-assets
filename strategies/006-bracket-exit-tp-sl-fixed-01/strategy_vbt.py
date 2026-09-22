import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    open_p = df['open'].values
    high_p = df['high'].values
    low_p = df['low'].values
    close_p = df['close'].values
    n = len(df)

    if 'timestamp' in df.columns:
        dt = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
    else:
        dt = pd.to_datetime(df.index, utc=True)

    hours = dt.dt.hour.values
    minutes = dt.dt.minute.values

    @njit
    def logic_loop(open_p, high_p, low_p, close_p, hours, minutes, fees):
        entries = np.zeros(n, dtype=np.bool_)
        exits = np.zeros(n, dtype=np.bool_)
        exec_price = np.zeros(n, dtype=np.float64)

        pos = 0
        entry_price = 0.0
        stop_price = 0.0
        take_price = 0.0

        for i in range(1, n):
            h_prev = hours[i-1]
            m_prev = minutes[i-1]

            # 1. Update position status / exits
            if pos == 1:
                exit_long = False
                exit_px = 0.0

                if h_prev == 6 and m_prev == 15:
                    exit_long = True
                    exit_px = open_p[i]
                elif low_p[i] <= stop_price:
                    exit_long = True
                    exit_px = stop_price
                elif high_p[i] >= take_price:
                    exit_long = True
                    exit_px = take_price

                if exit_long:
                    exits[i] = True
                    exec_price[i] = exit_px
                    pos = 0

            # 2. Check entries
            if pos == 0:
                if h_prev == 0 and m_prev == 15:
                    entries[i] = True
                    exec_price[i] = open_p[i]
                    pos = 1
                    entry_price = open_p[i]
                    stop_price = entry_price * 0.996
                    take_price = entry_price * 1.004

        return entries, exits, exec_price

    entries, exits, exec_price = logic_loop(
        open_p, high_p, low_p, close_p, hours, minutes, fees
    )

    price_series = pd.Series(exec_price, index=df.index)
    price_series = price_series.where(price_series > 0, df['open'])

    return vbt.Portfolio.from_signals(
        df['close'],
        entries=pd.Series(entries, index=df.index),
        exits=pd.Series(exits, index=df.index),
        price=price_series,
        init_cash=1000000,
        fees=fees,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
