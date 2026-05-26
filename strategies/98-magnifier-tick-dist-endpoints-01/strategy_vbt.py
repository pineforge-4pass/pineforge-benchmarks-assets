import pandas as pd
import numpy as np
import vectorbt as vbt

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    open_p = df['open'].values
    high_p = df['high'].values
    low_p = df['low'].values
    close_p = df['close'].values
    n = len(df)

    # Calculate indicators
    emaFast = df['close'].ewm(span=9, adjust=False).mean()
    emaSlow = df['close'].ewm(span=21, adjust=False).mean()

    entry_signal_series = (emaFast > emaSlow) & (emaFast.shift(1) <= emaSlow.shift(1))
    exit_signal_series = (emaFast < emaSlow) & (emaFast.shift(1) >= emaSlow.shift(1))

    entryCond = entry_signal_series.values
    exitCond = exit_signal_series.values

    # Pre-calculate stop levels for each bar if an entry occurs on that bar
    stop_lvls = open_p + (high_p - open_p) * 0.5

    entries = np.zeros(n, dtype=np.bool_)
    exits = np.zeros(n, dtype=np.bool_)
    short_entries = np.zeros(n, dtype=np.bool_)
    short_exits = np.zeros(n, dtype=np.bool_)
    execution_prices = open_p.copy()

    pos = 0
    stop_val = np.nan

    for i in range(1, n):
        # 1. Process entry signal from previous bar
        if entryCond[i-1] and pos == 0:
            entries[i] = True
            pos = 1
            stop_val = stop_lvls[i-1]
            execution_prices[i] = open_p[i]

        # 2. Process exit logic for current bar
        if pos == 1:
            # Check exitCond from previous bar
            if exitCond[i-1]:
                exits[i] = True
                pos = 0
                execution_prices[i] = open_p[i]
                stop_val = np.nan
            elif not np.isnan(stop_val):
                # Check stop loss
                if open_p[i] <= stop_val:
                    exits[i] = True
                    pos = 0
                    execution_prices[i] = open_p[i]
                    stop_val = np.nan
                elif low_p[i] <= stop_val:
                    exits[i] = True
                    pos = 0
                    execution_prices[i] = stop_val
                    stop_val = np.nan

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
