import pandas as pd
import numpy as np
import vectorbt as vbt

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close_series = df['close']
    open_p = df['open'].values
    high_p = df['high'].values
    low_p = df['low'].values
    close_p = df['close'].values
    n = len(open_p)

    ma = close_series.ewm(span=20, adjust=False).mean().values

    prev_close = close_series.shift(1)
    tr1 = df['high'] - df['low']
    tr2 = (df['high'] - prev_close).abs()
    tr3 = (df['low'] - prev_close).abs()
    tr = np.maximum(tr1, np.maximum(tr2, tr3))
    rangema = tr.ewm(alpha=1/10, adjust=False).mean().values

    upper = ma + 2.0 * rangema
    lower = ma - 2.0 * rangema

    crossUpper = np.zeros(n, dtype=np.bool_)
    crossLower = np.zeros(n, dtype=np.bool_)
    for i in range(1, n):
        crossUpper[i] = (close_p[i] > upper[i]) and (close_p[i-1] <= upper[i-1])
        crossLower[i] = (close_p[i] < lower[i]) and (close_p[i-1] >= lower[i-1])

    entries = np.zeros(n, dtype=np.bool_)
    short_entries = np.zeros(n, dtype=np.bool_)
    exits = np.zeros(n, dtype=np.bool_)
    short_exits = np.zeros(n, dtype=np.bool_)
    execution_prices = open_p.copy()

    pos = 0

    long_order_active = False
    long_stop_price = np.nan
    short_order_active = False
    short_stop_price = np.nan

    bprice = 0.0
    sprice = 0.0
    crossBcond = False
    crossScond = False

    for i in range(1, n):
        filled_long = False
        filled_short = False
        fill_p = 0.0

        if long_order_active and pos <= 0:
            if open_p[i] >= long_stop_price:
                fill_p = open_p[i]
                filled_long = True
            elif high_p[i] >= long_stop_price:
                fill_p = long_stop_price
                filled_long = True

        if short_order_active and pos >= 0 and not filled_long:
            if open_p[i] <= short_stop_price:
                fill_p = open_p[i]
                filled_short = True
            elif low_p[i] <= short_stop_price:
                fill_p = short_stop_price
                filled_short = True

        if filled_long:
            if pos == -1:
                short_exits[i] = True
            entries[i] = True
            execution_prices[i] = fill_p
            pos = 1
            long_order_active = False

        elif filled_short:
            if pos == 1:
                exits[i] = True
            short_entries[i] = True
            execution_prices[i] = fill_p
            pos = -1
            short_order_active = False

        crossUpper_val = crossUpper[i]
        crossLower_val = crossLower[i]

        bprice = high_p[i] + 0.01 if crossUpper_val else bprice
        sprice = low_p[i] - 0.01 if crossLower_val else sprice

        crossBcond = True if crossUpper_val else crossBcond
        crossScond = True if crossLower_val else crossScond

        cancelBcond = crossBcond and (close_p[i] < ma[i] or high_p[i] >= bprice)
        cancelScond = crossScond and (close_p[i] > ma[i] or low_p[i] <= sprice)

        if cancelBcond:
            long_order_active = False
        if crossUpper_val:
            long_order_active = True
            long_stop_price = bprice

        if cancelScond:
            short_order_active = False
        if crossLower_val:
            short_order_active = True
            short_stop_price = sprice

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
