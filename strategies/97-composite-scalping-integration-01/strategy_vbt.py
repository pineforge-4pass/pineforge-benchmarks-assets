import pandas as pd
import numpy as np
import vectorbt as vbt
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    open_p = df['open'].values
    high_p = df['high'].values
    low_p = df['low'].values
    close_p = df['close'].values
    n = len(df)

    # Calculate EMA indicators
    ema_fast = df['close'].ewm(span=5, adjust=False).mean()
    ema_slow = df['close'].ewm(span=13, adjust=False).mean()

    long_signal_series = (ema_fast > ema_slow) & (ema_fast.shift(1) <= ema_slow.shift(1))
    short_signal_series = (ema_fast < ema_slow) & (ema_fast.shift(1) >= ema_slow.shift(1))

    long_signals = long_signal_series.values
    short_signals = short_signal_series.values

    entries = np.zeros(n, dtype=np.bool_)
    short_entries = np.zeros(n, dtype=np.bool_)
    exits = np.zeros(n, dtype=np.bool_)
    short_exits = np.zeros(n, dtype=np.bool_)
    execution_prices = open_p.copy()

    pos = 0
    tp_price = np.nan
    sl_price = np.nan
    mintick = 0.01

    for i in range(1, n):
        # 1. Process entry signals from previous bar
        if long_signals[i-1] and pos <= 0:
            entries[i] = True
            pos = 1
            entry_px = open_p[i]
            tp_price = entry_px + 15 * mintick
            sl_price = entry_px - 7 * mintick
            execution_prices[i] = entry_px
        elif short_signals[i-1] and pos >= 0:
            short_entries[i] = True
            pos = -1
            entry_px = open_p[i]
            tp_price = entry_px - 15 * mintick
            sl_price = entry_px + 7 * mintick
            execution_prices[i] = entry_px

        # 2. Process exit logic for current bar (including the newly entered position)
        if pos != 0 and not np.isnan(tp_price):
            exited = False
            exit_p = 0.0

            if pos == 1:
                if open_p[i] >= tp_price:
                    exit_p = open_p[i]
                    exited = True
                elif open_p[i] <= sl_price:
                    exit_p = open_p[i]
                    exited = True
                elif low_p[i] <= sl_price and high_p[i] >= tp_price:
                    if open_p[i] >= close_p[i]:
                        exit_p = sl_price
                    else:
                        exit_p = tp_price
                    exited = True
                elif high_p[i] >= tp_price:
                    exit_p = tp_price
                    exited = True
                elif low_p[i] <= sl_price:
                    exit_p = sl_price
                    exited = True
            elif pos == -1:
                if open_p[i] <= tp_price:
                    exit_p = open_p[i]
                    exited = True
                elif open_p[i] >= sl_price:
                    exit_p = open_p[i]
                    exited = True
                elif low_p[i] <= tp_price and high_p[i] >= sl_price:
                    if open_p[i] >= close_p[i]:
                        exit_p = tp_price
                    else:
                        exit_p = sl_price
                    exited = True
                elif low_p[i] <= tp_price:
                    exit_p = tp_price
                    exited = True
                elif high_p[i] >= sl_price:
                    exit_p = sl_price
                    exited = True

            if exited:
                if entries[i] or short_entries[i]:
                    if i + 1 < n:
                        if pos == 1:
                            exits[i+1] = True
                        else:
                            short_exits[i+1] = True
                        execution_prices[i+1] = exit_p
                else:
                    if pos == 1:
                        exits[i] = True
                    else:
                        short_exits[i] = True
                    execution_prices[i] = exit_p
                pos = 0
                tp_price = np.nan
                sl_price = np.nan

    return vbt.Portfolio.from_signals(
        df['close'],
        entries=pd.Series(entries, index=df.index),
        short_entries=pd.Series(short_entries, index=df.index),
        exits=pd.Series(exits, index=df.index),
        short_exits=pd.Series(short_exits, index=df.index),
        price=pd.Series(execution_prices, index=df.index),
        init_cash=1000000,
        fees=fees,
        slippage=0.0,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
