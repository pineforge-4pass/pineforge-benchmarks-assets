import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit

@njit
def volty_loop_nb(open_p, high_p, low_p, close_p, atrs, length):
    n = len(close_p)
    entries = np.zeros(n, dtype=np.bool_)
    short_entries = np.zeros(n, dtype=np.bool_)
    prices = np.zeros(n, dtype=np.float64)

    pos = 0 # 0: flat, 1: long, -1: short
    for i in range(1, n):
        if i - 1 < length:
            continue
        atrs_prev = atrs[i-1]
        close_prev = close_p[i-1]
        if np.isnan(atrs_prev) or np.isnan(close_prev):
            continue

        stop_long = close_prev + atrs_prev
        stop_short = close_prev - atrs_prev

        long_trig = high_p[i] >= stop_long
        short_trig = low_p[i] <= stop_short

        if pos == 1:
            if short_trig:
                short_entries[i] = True
                prices[i] = min(open_p[i], stop_short)
                pos = -1
        elif pos == -1:
            if long_trig:
                entries[i] = True
                prices[i] = max(open_p[i], stop_long)
                pos = 1
        else: # pos == 0
            if long_trig and short_trig:
                if open_p[i] >= stop_long:
                    entries[i] = True
                    prices[i] = max(open_p[i], stop_long)
                    pos = 1
                elif open_p[i] <= stop_short:
                    short_entries[i] = True
                    prices[i] = min(open_p[i], stop_short)
                    pos = -1
                else:
                    if close_p[i] >= open_p[i]:
                        entries[i] = True
                        prices[i] = max(open_p[i], stop_long)
                        pos = 1
                    else:
                        short_entries[i] = True
                        prices[i] = min(open_p[i], stop_short)
                        pos = -1
            elif long_trig:
                entries[i] = True
                prices[i] = max(open_p[i], stop_long)
                pos = 1
            elif short_trig:
                short_entries[i] = True
                prices[i] = min(open_p[i], stop_short)
                pos = -1

    return entries, short_entries, prices

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    high = df['high']
    low = df['low']
    close = df['close']
    open_val = df['open']
    length = 5
    numATRs = 0.75

    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs().fillna(0.0)
    tr3 = (low - prev_close).abs().fillna(0.0)
    tr = np.maximum(tr1, np.maximum(tr2, tr3))

    atrs = (tr.rolling(length).mean() * numATRs).values

    entries, short_entries, prices = volty_loop_nb(
        open_val.values,
        high.values,
        low.values,
        close.values,
        atrs,
        length
    )

    # Convert prices to Series, filling 0 with open price so vbt doesn't fail or use 0
    prices_ser = pd.Series(prices, index=df.index)
    prices_ser = prices_ser.where(prices_ser > 0, open_val)

    return vbt.Portfolio.from_signals(
        close,
        entries=pd.Series(entries, index=df.index),
        short_entries=pd.Series(short_entries, index=df.index),
        price=prices_ser,
        init_cash=1000000,
        fees=fees,
        slippage=0.0,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
