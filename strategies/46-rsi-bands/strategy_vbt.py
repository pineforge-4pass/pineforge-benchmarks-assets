import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit
from speed.vbt_helpers import rsi

@njit
def logic_loop(rsi_val, bb_mid, bb_dn, bb_up):
    n = len(rsi_val)
    entries = np.zeros(n, dtype=np.bool_)
    short_entries = np.zeros(n, dtype=np.bool_)
    exits = np.zeros(n, dtype=np.bool_)
    short_exits = np.zeros(n, dtype=np.bool_)

    pos = 0 # 0: flat, 1: long, -1: short

    for i in range(2, n):
        # 1. Evaluate exits based on previous bar
        if pos == 1 and rsi_val[i-1] > bb_mid[i-1]:
            exits[i] = True
            pos = 0
        elif pos == -1 and rsi_val[i-1] < bb_mid[i-1]:
            short_exits[i] = True
            pos = 0

        # 2. Evaluate entries based on previous bar
        longCond = rsi_val[i-1] < bb_dn[i-1] and rsi_val[i-1] > rsi_val[i-2]
        shortCond = rsi_val[i-1] > bb_up[i-1] and rsi_val[i-1] < rsi_val[i-2]

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
    bbLen = 50
    bbMult = 2.0

    # Indicators
    rsiVal = rsi(close, rsiLen)
    rsiBBMid = rsiVal.rolling(bbLen).mean()
    rsiDev = rsiVal.rolling(bbLen).std(ddof=0) * bbMult
    rsiBBUp = rsiBBMid + rsiDev
    rsiBBDn = rsiBBMid - rsiDev

    entries, short_entries, exits, short_exits = logic_loop(
        rsiVal.values, rsiBBMid.values, rsiBBDn.values, rsiBBUp.values
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
