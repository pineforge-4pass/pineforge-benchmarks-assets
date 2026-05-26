import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit
from speed.vbt_helpers import atr

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close = df['close'].values
    high = df['high'].values
    low = df['low'].values
    open_val = df['open'].values
    n = len(df)

    lookback = 20
    structureLen = 5
    atrLen = 14
    atrMult = 1.5
    rr = 2.0

    # 1. Compute recentHigh, recentLow, structureHigh, structureLow, atrValue
    # recentHigh[i] = ta.highest(high[1], lookback) -> high[i-lookback:i]
    # recentLow[i] = ta.lowest(low[1], lookback) -> low[i-lookback:i]
    # structureHigh[i] = ta.highest(high, structureLen) -> high[i-structureLen+1:i+1]
    # structureLow[i] = ta.lowest(low, structureLen) -> low[i-structureLen+1:i+1]

    # Calculate ATR using vbt_helpers
    atr_val = atr(df['high'], df['low'], df['close'], atrLen).fillna(0).values

    # Precompute rolling highest/lowest in python/numpy to avoid slow python loops or numba complexity
    recentHigh = df['high'].shift(1).rolling(lookback).max().fillna(0).values
    recentLow = df['low'].shift(1).rolling(lookback).min().fillna(0).values

    structureHigh = df['high'].rolling(structureLen).max().fillna(0).values
    structureLow = df['low'].rolling(structureLen).min().fillna(0).values

    # Sweep detection
    # sweepHigh = high > recentHigh and close < recentHigh
    # sweepLow  = low < recentLow and close > recentLow
    sweepHigh = (high > recentHigh) & (close < recentHigh)
    sweepLow = (low < recentLow) & (close > recentLow)

    # Structure break
    # bullStructureBreak = close > structureHigh[1] -> structureHigh[i-1]
    # bearStructureBreak = close < structureLow[1] -> structureLow[i-1]

    @njit
    def simulate_liquidity_sweep(close, open_val, sweepHigh, sweepLow, structureHigh, structureLow, atr_val):
        entries = np.zeros(n, dtype=np.bool_)
        short_entries = np.zeros(n, dtype=np.bool_)
        exits = np.zeros(n, dtype=np.bool_)
        short_exits = np.zeros(n, dtype=np.bool_)
        exec_price = np.zeros(n, dtype=np.float64)

        pos = 0
        entry_price = 0.0
        stop_price = 0.0
        take_price = 0.0

        for i in range(2, n):
            # Check signals from previous bar (process_orders_on_close = false, entries on next bar's open)
            sh_prev = sweepHigh[i-1]
            sl_prev = sweepLow[i-1]
            atr_prev = atr_val[i-1]

            bullStructureBreak = close[i-1] > structureHigh[i-2]
            bearStructureBreak = close[i-1] < structureLow[i-2]

            # Entry triggers on bar i
            longCondition = sl_prev and bullStructureBreak
            shortCondition = sh_prev and bearStructureBreak

            if pos == 1:
                # Check exit on bar i (using high/low of bar i)
                # Since we check if low <= stop_price, or high >= take_price
                # Exit takes priority.
                # Pine Script strategy.exit evaluates intraday. If both hit, usually stop is hit first (or depends).
                # Here we check stop first, then limit.
                exit_long = False
                exit_price = 0.0

                # Check if stop is hit
                if low[i] <= stop_price:
                    exit_long = True
                    exit_price = stop_price
                elif high[i] >= take_price:
                    exit_long = True
                    exit_price = take_price

                if exit_long:
                    exits[i] = True
                    exec_price[i] = exit_price
                    pos = 0

            elif pos == -1:
                exit_short = False
                exit_price = 0.0

                if high[i] <= stop_price: # wait, for short stop is ABOVE price, so high[i] >= stop_price
                    pass
                if high[i] >= stop_price:
                    exit_short = True
                    exit_price = stop_price
                elif low[i] <= take_price:
                    exit_short = True
                    exit_price = take_price

                if exit_short:
                    short_exits[i] = True
                    exec_price[i] = exit_price
                    pos = 0

            # If no position, we can enter on bar i at open_val[i]
            if pos == 0:
                if longCondition:
                    entries[i] = True
                    exec_price[i] = open_val[i]
                    pos = 1
                    entry_price = open_val[i]
                    stop_price = entry_price - atr_prev * atrMult
                    take_price = entry_price + atr_prev * atrMult * rr
                elif shortCondition:
                    short_entries[i] = True
                    exec_price[i] = open_val[i]
                    pos = -1
                    entry_price = open_val[i]
                    stop_price = entry_price + atr_prev * atrMult
                    take_price = entry_price - atr_prev * atrMult * rr

        return entries, short_entries, exits, short_exits, exec_price

    entries, short_entries, exits, short_exits, exec_price = simulate_liquidity_sweep(
        close, open_val, sweepHigh, sweepLow, structureHigh, structureLow, atr_val
    )

    # Make sure we pass the prices where trade actually happens to vbt
    # If exec_price is 0, vbt will fall back to close or open, but for non-zero entries/exits we must provide price.
    # To do this safely, we can create a Series for price where we fill non-zero exec_prices, and close elsewhere.
    price_series = pd.Series(exec_price, index=df.index)
    price_series = price_series.where(price_series > 0, df['open'])

    return vbt.Portfolio.from_signals(
        df['close'],
        entries=pd.Series(entries, index=df.index),
        short_entries=pd.Series(short_entries, index=df.index),
        exits=pd.Series(exits, index=df.index),
        short_exits=pd.Series(short_exits, index=df.index),
        price=price_series,
        init_cash=1000000,
        fees=fees,
        slippage=0.0,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
