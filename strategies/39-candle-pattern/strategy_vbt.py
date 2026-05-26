import pandas as pd
import numpy as np
import vectorbt as vbt

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    high = df['high']
    low = df['low']
    close = df['close']
    open_val = df['open']

    trendLen = 20
    trendMA = close.rolling(trendLen).mean()
    upTrend = close > trendMA
    dnTrend = close < trendMA

    bodySize = (close - open_val).abs()
    upperWick = high - np.maximum(open_val, close)
    lowerWick = np.minimum(open_val, close) - low
    totalRange = high - low

    bullEngulf = (close > open_val) & (close.shift(1) < open_val.shift(1)) & (close > open_val.shift(1)) & (open_val < close.shift(1))
    bearEngulf = (close < open_val) & (close.shift(1) > open_val.shift(1)) & (close < open_val.shift(1)) & (open_val > close.shift(1))

    hammer = (lowerWick > bodySize * 2) & (upperWick < bodySize * 0.5) & (bodySize > 0)
    shootStar = (upperWick > bodySize * 2) & (lowerWick < bodySize * 0.5) & (bodySize > 0)

    morningStar = (close.shift(2) < open_val.shift(2)) & (bodySize.shift(1) < bodySize.shift(2) * 0.3) & (close > open_val) & (close > (open_val.shift(2) + close.shift(2)) / 2)

    bullSignal = (bullEngulf | hammer | morningStar) & dnTrend
    bearSignal = (bearEngulf | shootStar) & upTrend

    entries = bullSignal.shift(1).fillna(False)
    short_entries = bearSignal.shift(1).fillna(False)

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
