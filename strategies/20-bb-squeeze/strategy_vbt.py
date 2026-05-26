import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit
from speed.vbt_helpers import linreg

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close = df['close']
    open_val = df['open']

    bbMid = close.rolling(20).mean()
    bbDev = close.rolling(20).std(ddof=0)
    bbUpper = bbMid + 2.0 * bbDev
    bbLower = bbMid - 2.0 * bbDev

    middle_ema = close.ewm(span=20, adjust=False).mean()
    prev_close = close.shift(1)
    tr = np.maximum(df['high'] - df['low'], np.maximum((df['high'] - prev_close).abs(), (df['low'] - prev_close).abs()))
    tr = pd.Series(tr, index=close.index)
    range_ema = tr.ewm(span=20, adjust=False).mean()
    kcUpper = middle_ema + 1.5 * range_ema
    kcLower = middle_ema - 1.5 * range_ema

    sqzOn = (bbLower > kcLower) & (bbUpper < kcUpper)
    sqzOff = (bbLower < kcLower) | (bbUpper > kcUpper)

    mom = linreg(close - bbMid, 20, 0)

    @njit
    def sqz_fired_nb(sqz_on, sqz_off, mom):
        n = len(sqz_on)
        entries = np.zeros(n, dtype=np.bool_)
        short_entries = np.zeros(n, dtype=np.bool_)

        was_squeezed = False
        for i in range(1, n):
            if sqz_on[i]:
                was_squeezed = True

            sqz_fired = was_squeezed and sqz_off[i]
            if sqz_fired and mom[i] > 0:
                entries[i] = True
                was_squeezed = False
            elif sqz_fired and mom[i] < 0:
                short_entries[i] = True
                was_squeezed = False

        return entries, short_entries

    entries, short_entries = sqz_fired_nb(
        sqzOn.values.astype(np.bool_),
        sqzOff.values.astype(np.bool_),
        mom.values.astype(np.float64)
    )
    entries = pd.Series(entries, index=close.index)
    short_entries = pd.Series(short_entries, index=close.index)

    exits = mom < 0
    short_exits = mom > 0

    return vbt.Portfolio.from_signals(
        close,
        entries=entries.shift(1).fillna(False),
        short_entries=short_entries.shift(1).fillna(False),
        exits=exits.shift(1).fillna(False),
        short_exits=short_exits.shift(1).fillna(False),
        price=open_val,
        init_cash=1000000,
        fees=fees,
        slippage=0.0,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
