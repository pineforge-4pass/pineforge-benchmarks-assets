import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit
from speed.vbt_helpers import atr, dmi

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close = df['close'].values
    high = df['high'].values
    low = df['low'].values
    open_val = df['open'].values
    n = len(df)

    emaFast = 50
    emaSlow = 200
    rsiLen = 3
    rsiOB = 80
    rsiOS = 20
    adxLen = 5
    adxLevel = 20
    atrLen = 14
    atrMult = 1.2

    # EMA calculations using pandas
    ema50 = df['close'].ewm(span=emaFast, adjust=False).mean().values
    ema200 = df['close'].ewm(span=emaSlow, adjust=False).mean().values

    # RSI calculation using speed.vbt_helpers
    from speed.vbt_helpers import rsi
    rsi_val = rsi(df['close'], rsiLen).fillna(50.0).values

    # DMI/ADX using speed.vbt_helpers
    _, _, adx = dmi(df['high'], df['low'], df['close'], adxLen, adxLen)
    adx_val = adx.fillna(0.0).values

    # ATR using speed.vbt_helpers
    atr_val = atr(df['high'], df['low'], df['close'], atrLen).fillna(0.0).values

    # Candle strength
    body = np.abs(close - open_val)
    candleRange = high - low
    # Avoid division by zero by setting range to 1.0 where it is 0.0
    safeRange = np.where(candleRange == 0.0, 1.0, candleRange)
    strongBull = (close > open_val) & (body > safeRange * 0.5)
    strongBear = (close < open_val) & (body > safeRange * 0.5)

    # Trend filter
    trendLong = (close > ema50) & (ema50 > ema200)
    trendShort = (close < ema50) & (ema50 < ema200)

    # RSI Crossover/Crossunder
    # rsiLong = ta.crossover(rsi, rsiOS) -> rsi[i] > rsiOS and rsi[i-1] <= rsiOS
    # rsiShort = ta.crossunder(rsi, rsiOB) -> rsi[i] < rsiOB and rsi[i-1] >= rsiOB
    rsiLong = np.zeros(n, dtype=np.bool_)
    rsiShort = np.zeros(n, dtype=np.bool_)
    for i in range(1, n):
        rsiLong[i] = (rsi_val[i] > rsiOS) and (rsi_val[i-1] <= rsiOS)
        rsiShort[i] = (rsi_val[i] < rsiOB) and (rsi_val[i-1] >= rsiOB)

    trendStrength = adx_val > adxLevel

    # Entry conditions
    longCondition = trendLong & rsiLong & trendStrength & strongBull
    shortCondition = trendShort & rsiShort & trendStrength & strongBear

    @njit
    def simulate_scalping(close, open_val, high, low, longCondition, shortCondition, atr_val):
        entries = np.zeros(n, dtype=np.bool_)
        short_entries = np.zeros(n, dtype=np.bool_)
        exits = np.zeros(n, dtype=np.bool_)
        short_exits = np.zeros(n, dtype=np.bool_)
        exec_price = np.zeros(n, dtype=np.float64)

        pos = 0
        entry_price = 0.0
        stop_price = 0.0
        take_price = 0.0

        # Trailing stop params
        trail_active = False
        highest_high = 0.0
        lowest_low = 9999999.0
        trail_points = 0.0

        for i in range(1, n):
            lc_prev = longCondition[i-1]
            sc_prev = shortCondition[i-1]
            atr_prev = atr_val[i-1]

            if pos == 1:
                # Update trailing stop / check exit
                # Pine's strategy.exit with stop, limit and trail_points
                # "trail_points" activates trailing stop when price moves in favor by trail_points.
                # In Pine, trail_points=atr means trailing starts when price moves up by 1 ATR from entry.
                # Once activated, stop trails the highest high by trail_points (atr).
                # Actually, in Pine Script, trail_points specifies the distance from the current price to activate trailing,
                # and trail_offset specifies the trailing distance. If trail_offset is not specified, it defaults to trail_points.
                # So once price hits entry_price + atr, trailing stop is activated at entry_price (since trail_offset = atr, i.e. highest_high - atr).
                # Prior to activation, standard stop_price is active.

                # Check highest high reached since entry
                if high[i] > highest_high:
                    highest_high = high[i]

                if not trail_active:
                    # Check if trailing is activated
                    if highest_high >= entry_price + trail_points:
                        trail_active = True
                        stop_price = highest_high - trail_points
                else:
                    # Trail the stop
                    current_stop = highest_high - trail_points
                    if current_stop > stop_price:
                        stop_price = current_stop

                exit_long = False
                exit_price = 0.0

                # Check if stop is hit
                if low[i] <= stop_price:
                    exit_long = True
                    exit_price = stop_price
                elif high[i] >= take_price and not trail_active: # limit is usually disabled once trailing is active? Or not?
                    # In Pine, if both limit and trail are specified, limit can still be hit. But standard trailing stop usually has limit.
                    # Let's check limit first if not hit stop.
                    exit_long = True
                    exit_price = take_price

                if exit_long:
                    exits[i] = True
                    exec_price[i] = exit_price
                    pos = 0
                    trail_active = False

            elif pos == -1:
                if low[i] < lowest_low:
                    lowest_low = low[i]

                if not trail_active:
                    if lowest_low <= entry_price - trail_points:
                        trail_active = True
                        stop_price = lowest_low + trail_points
                else:
                    current_stop = lowest_low + trail_points
                    if current_stop < stop_price:
                        stop_price = current_stop

                exit_short = False
                exit_price = 0.0

                if high[i] >= stop_price:
                    exit_short = True
                    exit_price = stop_price
                elif low[i] <= take_price and not trail_active:
                    exit_short = True
                    exit_price = take_price

                if exit_short:
                    short_exits[i] = True
                    exec_price[i] = exit_price
                    pos = 0
                    trail_active = False

            if pos == 0:
                if lc_prev:
                    entries[i] = True
                    exec_price[i] = open_val[i]
                    pos = 1
                    entry_price = open_val[i]
                    stop_price = entry_price - atr_prev * atrMult
                    take_price = entry_price + (entry_price - stop_price) * 2
                    highest_high = open_val[i]
                    trail_active = False
                    trail_points = atr_prev
                elif sc_prev:
                    short_entries[i] = True
                    exec_price[i] = open_val[i]
                    pos = -1
                    entry_price = open_val[i]
                    stop_price = entry_price + atr_prev * atrMult
                    take_price = entry_price - (stop_price - entry_price) * 2
                    lowest_low = open_val[i]
                    trail_active = False
                    trail_points = atr_prev

        return entries, short_entries, exits, short_exits, exec_price

    entries, short_entries, exits, short_exits, exec_price = simulate_scalping(
        close, open_val, high, low, longCondition, shortCondition, atr_val
    )

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
