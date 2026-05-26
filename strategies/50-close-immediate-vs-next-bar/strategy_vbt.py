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
    def logic_loop(open_p, close_p, hours, minutes):
        entries = np.zeros(n, dtype=np.bool_)
        exits = np.zeros(n, dtype=np.bool_)
        exec_price = np.zeros(n, dtype=np.float64)

        pos = 0 # 0: flat, 1: long

        for i in range(1, n):
            h_prev = hours[i-1]
            m_prev = minutes[i-1]

            # Normal entry: hour == 2 and minute == 15
            if pos == 0 and h_prev == 2 and m_prev == 15:
                entries[i] = True
                exec_price[i] = open_p[i]
                pos = 1

            # Normal close: hour == 3 and minute == 15
            elif pos == 1 and h_prev == 3 and m_prev == 15:
                exits[i] = True
                exec_price[i] = open_p[i]
                pos = 0

            # Immediate entry: hour == 10 and minute == 15
            elif pos == 0 and h_prev == 10 and m_prev == 15:
                entries[i] = True
                exec_price[i] = open_p[i]
                pos = 1

            # Immediate close: hour == 11 and minute == 15
            elif pos == 1 and h_prev == 11 and m_prev == 15:
                # Executes immediately at the close of bar i-1
                exits[i-1] = True
                exec_price[i-1] = close_p[i-1]
                pos = 0

        return entries, exits, exec_price

    entries, exits, exec_price = logic_loop(
        open_p, close_p, hours, minutes
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
