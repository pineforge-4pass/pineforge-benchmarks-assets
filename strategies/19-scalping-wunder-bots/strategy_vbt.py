import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit
from speed.vbt_helpers import atr as atr_helper

@njit
def pivothigh_nb(high: np.ndarray, left_bars: int, right_bars: int) -> np.ndarray:
    n = len(high)
    out = np.empty(n, dtype=np.float64)
    out[:] = np.nan
    total = left_bars + right_bars + 1
    for idx in range(n):
        if idx < total - 1:
            continue
        pivot = high[idx - right_bars]
        if np.isnan(pivot):
            continue

        ok = True
        for i in range(left_bars):
            val = high[idx - right_bars - left_bars + i]
            if np.isnan(val) or val > pivot:
                ok = False
                break
        if not ok:
            continue

        for i in range(right_bars):
            val = high[idx - right_bars + 1 + i]
            if np.isnan(val) or val >= pivot:
                ok = False
                break
        if ok:
            out[idx] = pivot
    return out

@njit
def pivotlow_nb(low: np.ndarray, left_bars: int, right_bars: int) -> np.ndarray:
    n = len(low)
    out = np.empty(n, dtype=np.float64)
    out[:] = np.nan
    total = left_bars + right_bars + 1
    for idx in range(n):
        if idx < total - 1:
            continue
        pivot = low[idx - right_bars]
        if np.isnan(pivot):
            continue

        ok = True
        for i in range(left_bars):
            val = low[idx - right_bars - left_bars + i]
            if np.isnan(val) or val < pivot:
                ok = False
                break
        if not ok:
            continue

        for i in range(right_bars):
            val = low[idx - right_bars + 1 + i]
            if np.isnan(val) or val <= pivot:
                ok = False
                break
        if ok:
            out[idx] = pivot
    return out

@njit
def wunder_loop_nb(open_p, high_p, low_p, close_p, volume,
                   p_high, p_low,
                   bb_upper, bb_lower,
                   ma_bearish_cross, ma_bullish_cross,
                   vol_avg, atr_val, atr_avg, risk_reward):
    n = len(close_p)
    entries = np.zeros(n, dtype=np.bool_)
    short_entries = np.zeros(n, dtype=np.bool_)
    exits = np.zeros(n, dtype=np.bool_)
    short_exits = np.zeros(n, dtype=np.bool_)
    execution_prices = np.zeros(n, dtype=np.float64)

    resistance_level = np.nan
    support_level = np.nan

    pos = 0 # 0: flat, 1: long, -1: short
    stop_price = np.nan
    take_profit = np.nan

    for i in range(1, n):
        if not np.isnan(p_high[i-1]):
            resistance_level = p_high[i-1]
        if not np.isnan(p_low[i-1]):
            support_level = p_low[i-1]

        close_prev = close_p[i-1]
        sr_zone = close_prev * 0.003

        near_res = (not np.isnan(resistance_level)) and (abs(close_prev - resistance_level) <= sr_zone)
        near_sup = (not np.isnan(support_level)) and (abs(close_prev - support_level) <= sr_zone)

        bb_long = close_prev > bb_upper[i-1]
        bb_short = close_prev < bb_lower[i-1]

        ma_bear = ma_bearish_cross[i-1]
        ma_bull = ma_bullish_cross[i-1]

        v_ok = volume[i-1] >= vol_avg[i-1] * 1.2
        a_ok = atr_val[i-1] >= atr_avg[i-1] * 0.5

        l_score = (1 if near_res else 0) + (1 if bb_long else 0) + (1 if ma_bear else 0)
        s_score = (1 if near_sup else 0) + (1 if bb_short else 0) + (1 if ma_bull else 0)

        rev_long_cond = (l_score >= 2) and v_ok and a_ok
        rev_short_cond = (s_score >= 2) and v_ok and a_ok

        if pos == 1:
            if low_p[i] <= stop_price and high_p[i] >= take_profit:
                exits[i] = True
                execution_prices[i] = stop_price
                pos = 0
            elif low_p[i] <= stop_price:
                exits[i] = True
                execution_prices[i] = stop_price
                pos = 0
            elif high_p[i] >= take_profit:
                exits[i] = True
                execution_prices[i] = take_profit
                pos = 0
        elif pos == -1:
            if high_p[i] >= stop_price and low_p[i] <= take_profit:
                short_exits[i] = True
                execution_prices[i] = stop_price
                pos = 0
            elif high_p[i] >= stop_price:
                short_exits[i] = True
                execution_prices[i] = stop_price
                pos = 0
            elif low_p[i] <= take_profit:
                short_exits[i] = True
                execution_prices[i] = take_profit
                pos = 0

        if pos == 0:
            if rev_long_cond:
                entries[i] = True
                execution_prices[i] = open_p[i]
                pos = 1
                atr_stop = atr_val[i-1] * 1.5
                stop_price = close_prev - atr_stop
                take_profit = close_prev + atr_stop * risk_reward
            elif rev_short_cond:
                short_entries[i] = True
                execution_prices[i] = open_p[i]
                pos = -1
                atr_stop = atr_val[i-1] * 1.5
                stop_price = close_prev + atr_stop
                take_profit = close_prev - atr_stop * risk_reward

    return entries, short_entries, exits, short_exits, execution_prices

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    high = df['high']
    low = df['low']
    close = df['close']
    open_val = df['open']
    vol = df['volume']

    sr_lookback = 20
    risk_reward = 2.0

    p_high = pivothigh_nb(high.values, sr_lookback, sr_lookback)
    p_low = pivotlow_nb(low.values, sr_lookback, sr_lookback)

    bb_basis = close.rolling(20).mean()
    bb_dev = 2.0 * close.rolling(20).std(ddof=0)
    bb_upper = (bb_basis + bb_dev).values
    bb_lower = (bb_basis - bb_dev).values

    fast_ma = close.ewm(span=9, adjust=False).mean()
    slow_ma = close.ewm(span=21, adjust=False).mean()

    ma_bearish_cross = ((fast_ma < slow_ma) & (fast_ma.shift(1) >= slow_ma.shift(1))).values
    ma_bullish_cross = ((fast_ma > slow_ma) & (fast_ma.shift(1) <= slow_ma.shift(1))).values

    vol_avg = vol.rolling(20).mean().values
    atr_val = atr_helper(high, low, close, 14).fillna(0.0).values
    atr_avg = pd.Series(atr_val, index=df.index).rolling(50).mean().fillna(0.0).values

    entries, short_entries, exits, short_exits, prices = wunder_loop_nb(
        open_val.values,
        high.values,
        low.values,
        close.values,
        vol.values,
        p_high,
        p_low,
        bb_upper,
        bb_lower,
        ma_bearish_cross,
        ma_bullish_cross,
        vol_avg,
        atr_val,
        atr_avg,
        risk_reward
    )

    prices_ser = pd.Series(prices, index=df.index)
    prices_ser = prices_ser.where(prices_ser > 0, open_val)

    return vbt.Portfolio.from_signals(
        close,
        entries=pd.Series(entries, index=df.index),
        short_entries=pd.Series(short_entries, index=df.index),
        exits=pd.Series(exits, index=df.index),
        short_exits=pd.Series(short_exits, index=df.index),
        price=prices_ser,
        init_cash=1000000,
        fees=fees,
        slippage=0.0,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
