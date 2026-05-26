import pandas as pd
import numpy as np
import vectorbt as vbt

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    high = df['high']
    low = df['low']
    close = df['close']
    open_val = df['open']

    lookback = 4
    kUp = 0.5
    kDn = 0.5

    hh = high.rolling(lookback).max()
    lc = close.rolling(lookback).min()
    hc = close.rolling(lookback).max()
    ll = low.rolling(lookback).min()

    range1 = hh - lc
    range2 = hc - ll
    dualRange = np.maximum(range1, range2)

    upperBound = open_val + kUp * dualRange
    lowerBound = open_val - kDn * dualRange

    longCond = close > upperBound
    shortCond = close < lowerBound

    entries = longCond.shift(1).fillna(False)
    short_entries = shortCond.shift(1).fillna(False)

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
