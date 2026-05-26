import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit
from speed.vbt_helpers import supertrend, dmi

@njit
def logic_loop(in_uptrend, adx_strong):
    n = len(in_uptrend)
    entries = np.zeros(n, dtype=np.bool_)
    short_entries = np.zeros(n, dtype=np.bool_)
    exits = np.zeros(n, dtype=np.bool_)
    short_exits = np.zeros(n, dtype=np.bool_)

    pos = 0 # 0: flat, 1: long, -1: short

    for i in range(2, n):
        st_bull_prev = in_uptrend[i-1]
        st_bear_prev = not in_uptrend[i-1]

        # 1. Evaluate exits based on previous bar
        if pos == 1 and st_bear_prev:
            exits[i] = True
            pos = 0
        elif pos == -1 and st_bull_prev:
            short_exits[i] = True
            pos = 0

        # 2. Evaluate entries based on previous bar
        longCond = in_uptrend[i-1] and (not in_uptrend[i-2]) and adx_strong[i-1]
        shortCond = (not in_uptrend[i-1]) and in_uptrend[i-2] and adx_strong[i-1]

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
    # Parameters
    stFactor = 3.0
    stPeriod = 10
    diLen = 14
    adxSmooth = 14
    adxThresh = 20.0

    # Indicators
    _, in_uptrend = supertrend(df['high'], df['low'], df['close'], period=stPeriod, multiplier=stFactor)
    _, _, adxVal = dmi(df['high'], df['low'], df['close'], diLen, adxSmooth)

    adx_strong = adxVal > adxThresh

    entries, short_entries, exits, short_exits = logic_loop(
        in_uptrend.values, adx_strong.values
    )

    return vbt.Portfolio.from_signals(
        df['close'],
        entries=pd.Series(entries, index=df.index),
        short_entries=pd.Series(short_entries, index=df.index),
        exits=pd.Series(exits, index=df.index),
        short_exits=pd.Series(short_exits, index=df.index),
        price=df['open'],
        init_cash=1000000,
        fees=fees,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
