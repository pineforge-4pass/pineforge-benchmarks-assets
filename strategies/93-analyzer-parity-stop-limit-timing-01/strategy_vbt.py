import pandas as pd
import numpy as np
import vectorbt as vbt
from speed.vbt_helpers import rma

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    utc_time = pd.to_datetime(df['timestamp'], unit='ms').dt.tz_localize('UTC')
    h = utc_time.dt.hour.values
    m = utc_time.dt.minute.values

    close_s = df['close']
    high_s = df['high']
    low_s = df['low']
    prev_close = close_s.shift(1)
    tr = np.maximum(high_s - low_s, np.maximum((high_s - prev_close).abs(), (low_s - prev_close).abs()))

    # Exact Pine RMA implementation of ATR
    period = 14
    tr_vals = tr.values
    atr_val = np.empty(len(df))
    atr_val[:] = np.nan
    first_valid = 1
    sum_tr = 0.0
    for i in range(first_valid, first_valid + period):
        sum_tr += tr_vals[i]
    atr_val[first_valid + period - 1] = sum_tr / period
    alpha = 1.0 / period
    for i in range(first_valid + period, len(df)):
        atr_val[i] = alpha * tr_vals[i] + (1 - alpha) * atr_val[i-1]

    n = len(df)
    entries = np.zeros(n, dtype=np.bool_)
    exits = np.zeros(n, dtype=np.bool_)
    execution_prices = df['open'].values.copy()

    pos = 0
    stop_lvl = 0.0
    tp_lvl = 0.0

    for i in range(1, n):
        if pos == 0:
            at_entry_window = (h[i-1] == 0 or h[i-1] == 12) & (m[i-1] == 0)
            atr_ok = not np.isnan(atr_val[i-1])
            if at_entry_window and atr_ok:
                pos = 1
                entries[i] = True
                execution_prices[i] = df['open'].values[i]
                stop_lvl = df['close'].values[i-1] - atr_val[i-1] * 1.0
                tp_lvl = df['close'].values[i-1] + atr_val[i-1] * 2.0

        if pos == 1:
            open_val = df['open'].values[i]
            high_val = df['high'].values[i]
            low_val = df['low'].values[i]
            close_val = df['close'].values[i]

            exited = False
            exit_p = 0.0

            if open_val >= tp_lvl:
                exit_p = open_val
                exited = True
            elif open_val <= stop_lvl:
                exit_p = open_val
                exited = True
            elif low_val <= stop_lvl and high_val >= tp_lvl:
                if open_val >= close_val:
                    exit_p = stop_lvl
                else:
                    exit_p = tp_lvl
                exited = True
            elif high_val >= tp_lvl:
                exit_p = tp_lvl
                exited = True
            elif low_val <= stop_lvl:
                exit_p = stop_lvl
                exited = True

            if exited:
                exits[i] = True
                execution_prices[i] = exit_p
                pos = 0

    return vbt.Portfolio.from_signals(
        df['close'],
        entries=pd.Series(entries, index=df.index),
        exits=pd.Series(exits, index=df.index),
        price=pd.Series(execution_prices, index=df.index),
        init_cash=1000000,
        fees=fees,
        slippage=0.0,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
