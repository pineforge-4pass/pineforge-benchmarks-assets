import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit
from speed.vbt_helpers import rsi

@njit
def logic_loop(open_p, close_p, score):
    n = len(close_p)
    entries = np.zeros(n, dtype=np.bool_)
    short_entries = np.zeros(n, dtype=np.bool_)
    exits = np.zeros(n, dtype=np.bool_)
    short_exits = np.zeros(n, dtype=np.bool_)

    pos = 0 # 0: flat, 1: long, -1: short

    for i in range(2, n):
        # 1. Evaluate exits
        if pos == 1 and score[i-1] <= 0:
            exits[i] = True
            pos = 0
        elif pos == -1 and score[i-1] >= 0:
            short_exits[i] = True
            pos = 0

        # 2. Evaluate entries
        longCond = (score[i-1] >= 2) and (score[i-2] < 2)
        shortCond = (score[i-1] <= -2) and (score[i-2] > -2)

        if longCond:
            if pos == -1:
                short_exits[i] = True
                pos = 0
            if pos == 0:
                entries[i] = True
                pos = 1
        elif shortCond:
            if pos == 1:
                exits[i] = True
                pos = 0
            if pos == 0:
                short_entries[i] = True
                pos = -1

    return entries, short_entries, exits, short_exits

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close = df['close']
    open_val = df['open']

    # Parameters
    rsiLen = 14
    maLen = 20
    bbLen = 20
    bbMult = 2.0

    # Indicators
    rsiVal = rsi(close, rsiLen)
    emaVal = close.ewm(span=maLen, adjust=False).mean()
    bbMid = close.rolling(bbLen).mean()
    bbStd = close.rolling(bbLen).std(ddof=0)

    # Compute score
    score_rsi = np.zeros(len(close))
    score_rsi[rsiVal > 50.0] = 1.0
    score_rsi[rsiVal < 50.0] = -1.0

    score_ema = np.where(close > emaVal, 1.0, -1.0)
    score_bb = np.where(close > bbMid, 1.0, -1.0)

    score = score_rsi + score_ema + score_bb

    # Run stateful loop
    entries, short_entries, exits, short_exits = logic_loop(
        open_val.values, close.values, score
    )

    return vbt.Portfolio.from_signals(
        close,
        entries=pd.Series(entries, index=df.index),
        short_entries=pd.Series(short_entries, index=df.index),
        exits=pd.Series(exits, index=df.index),
        short_exits=pd.Series(short_exits, index=df.index),
        price=open_val,
        init_cash=1000000,
        fees=fees,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
