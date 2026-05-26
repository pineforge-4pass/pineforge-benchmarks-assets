import pandas as pd
import numpy as np
import vectorbt as vbt
from speed.vbt_helpers import rsi

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close = df['close']
    open_val = df['open']

    # 1. Calculate indicators
    rsi_val = rsi(close, 14)
    rsi_bullish = rsi_val > 55
    rsi_bearish = rsi_val < 45
    rsi_momentum_up = rsi_val > rsi_val.shift(3)
    rsi_momentum_dn = rsi_val < rsi_val.shift(3)

    macd_line = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
    macd_signal = macd_line.ewm(span=9, adjust=False).mean()
    macd_hist = macd_line - macd_signal

    macd_bullish = (macd_hist > 0) & (macd_hist > macd_hist.shift(1))
    macd_bearish = (macd_hist < 0) & (macd_hist < macd_hist.shift(1))

    # 2. Scores
    momentum_bull_score = rsi_bullish.astype(int) + rsi_momentum_up.astype(int) + macd_bullish.astype(int)
    momentum_bear_score = rsi_bearish.astype(int) + rsi_momentum_dn.astype(int) + macd_bearish.astype(int)

    # 3. Simulate stateful entries/exits
    n = len(df)
    entries = np.zeros(n, dtype=np.bool_)
    short_entries = np.zeros(n, dtype=np.bool_)

    bull_score_val = momentum_bull_score.values
    bear_score_val = momentum_bear_score.values

    pos = 0
    for i in range(1, n - 1):
        long_cond = (bull_score_val[i] >= 2) and (bull_score_val[i-1] < 2)
        short_cond = (bear_score_val[i] >= 2) and (bear_score_val[i-1] < 2)

        if pos <= 0 and long_cond:
            entries[i+1] = True
            pos = 1
        elif pos >= 0 and short_cond:
            short_entries[i+1] = True
            pos = -1

    return vbt.Portfolio.from_signals(
        close,
        entries=pd.Series(entries, index=df.index),
        short_entries=pd.Series(short_entries, index=df.index),
        price=open_val,
        init_cash=1000000,
        fees=fees,
        slippage=0.0,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
