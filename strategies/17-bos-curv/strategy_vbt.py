import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit
from speed.vbt_helpers import atr as atr_helper

@njit
def curved_supertrend_nb(close_p, upper_band, lower_band, radius_strength):
    n = len(close_p)
    supertrend = np.empty(n, dtype=np.float64)
    direction = np.empty(n, dtype=np.int32)
    trend_changed = np.zeros(n, dtype=np.bool_)

    supertrend[0] = lower_band[0]
    direction[0] = 1

    anchor_price = lower_band[0]
    velocity = 0.0
    bar_count = 1

    for i in range(1, n):
        close_val = close_p[i]
        up_b = upper_band[i]
        lo_b = lower_band[i]
        prev_st = supertrend[i-1]
        prev_dir = direction[i-1]

        if prev_dir == 1:
            if close_val < prev_st:
                st_temp = up_b
            else:
                st_temp = max(lo_b, prev_st)
        else:
            if close_val > prev_st:
                st_temp = lo_b
            else:
                st_temp = min(up_b, prev_st)

        dir_temp = prev_dir
        if close_val < st_temp:
            dir_temp = -1
        elif close_val > st_temp:
            dir_temp = 1

        direction[i] = dir_temp
        changed = (dir_temp != prev_dir)
        trend_changed[i] = changed

        if changed:
            anchor_price = st_temp
            velocity = 0.0
            bar_count = 0

        bar_count += 1
        velocity += radius_strength * bar_count

        if dir_temp == 1:
            supertrend[i] = anchor_price + velocity
        else:
            supertrend[i] = anchor_price - velocity

    return supertrend, direction, trend_changed

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    high = df['high']
    low = df['low']
    close = df['close']
    open_val = df['open']

    atr_val = atr_helper(high, low, close, 14)
    src = (high + low) / 2

    upper_band = (src + 2.0 * atr_val).values
    lower_band = (src - 2.0 * atr_val).values

    # In case of early NaN in ATR, fill with initial value or close
    mask = np.isnan(upper_band) | np.isnan(lower_band)
    upper_band[mask] = close.values[mask]
    lower_band[mask] = close.values[mask]

    _, direction, trend_changed = curved_supertrend_nb(
        close.values,
        upper_band,
        lower_band,
        0.002
    )

    buy_signal = trend_changed & (direction == 1)
    sell_signal = trend_changed & (direction == -1)

    entries = pd.Series(buy_signal, index=df.index).shift(1).fillna(False)
    short_entries = pd.Series(sell_signal, index=df.index).shift(1).fillna(False)

    return vbt.Portfolio.from_signals(
        close,
        entries=entries,
        short_entries=short_entries,
        price=open_val,
        init_cash=1000000,
        fees=fees,
        slippage=0.0,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
