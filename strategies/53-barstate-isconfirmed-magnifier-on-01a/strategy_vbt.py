import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close_p = df['close'].values
    open_p = df['open'].values
    n = len(df)

    @njit
    def compute_ema(arr, length):
        out = np.empty(len(arr))
        out[:] = np.nan
        if len(arr) < length:
            return out
        sma_init = 0.0
        for i in range(length):
            sma_init += arr[i]
        sma_init /= length
        out[length-1] = sma_init
        alpha = 2.0 / (length + 1)
        for i in range(length, len(arr)):
            out[i] = alpha * arr[i] + (1 - alpha) * out[i-1]
        return out

    emaFast = compute_ema(close_p, 9)
    emaSlow = compute_ema(close_p, 21)

    @njit
    def logic_loop(close_p, open_p, emaFast, emaSlow):
        entries = np.zeros(n, dtype=np.bool_)
        short_entries = np.zeros(n, dtype=np.bool_)
        exits = np.zeros(n, dtype=np.bool_)
        short_exits = np.zeros(n, dtype=np.bool_)

        pendingLong = False
        pendingExit = False
        pos = 0

        for i in range(1, n):
            if np.isnan(emaFast[i-1]) or np.isnan(emaSlow[i-1]) or np.isnan(emaFast[i-2]) or np.isnan(emaSlow[i-2]):
                continue

            crossover = (emaFast[i-1] > emaSlow[i-1]) and (emaFast[i-2] <= emaSlow[i-2])
            crossunder = (emaFast[i-1] < emaSlow[i-1]) and (emaFast[i-2] >= emaSlow[i-2])

            if crossover:
                pendingLong = True
            if crossunder:
                pendingExit = True

            if pendingLong and pos == 0:
                entries[i] = True
                pos = 1
                pendingLong = False

            if pendingExit and pos > 0:
                exits[i] = True
                pos = 0
                pendingExit = False

        return entries, short_entries, exits, short_exits

    entries, short_entries, exits, short_exits = logic_loop(close_p, open_p, emaFast, emaSlow)

    return vbt.Portfolio.from_signals(
        df['close'],
        entries=pd.Series(entries, index=df.index),
        short_entries=pd.Series(short_entries, index=df.index),
        exits=pd.Series(exits, index=df.index),
        short_exits=pd.Series(short_exits, index=df.index),
        price=df['open'],
        init_cash=1000000,
        fees=fees,
        slippage=0.0,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
