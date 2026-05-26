import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    high_p = df['high'].values
    low_p = df['low'].values
    close_p = df['close'].values
    open_p = df['open'].values
    n = len(df)

    @njit
    def atr_stop_loop_nb(high_p, low_p, close_p, open_p):
        tr = np.empty(n)
        tr[0] = high_p[0] - low_p[0]
        for i in range(1, n):
            tr[i] = max(high_p[i] - low_p[i], abs(high_p[i] - close_p[i-1]), abs(low_p[i] - close_p[i-1]))
        atr_val = np.empty(n)
        atr_val[:] = np.nan
        atr_val[13] = np.mean(tr[:14])
        for i in range(14, n):
            atr_val[i] = (1/14) * tr[i] + (1 - 1/14) * atr_val[i-1]

        ma_val = np.empty(n)
        ma_val[:] = np.nan
        ma_val[19] = np.mean(close_p[:20])
        alpha_ema = 2 / 21
        for i in range(20, n):
            ma_val[i] = alpha_ema * close_p[i] + (1 - alpha_ema) * ma_val[i-1]

        entries = np.zeros(n, dtype=np.bool_)
        short_entries = np.zeros(n, dtype=np.bool_)
        exits = np.zeros(n, dtype=np.bool_)
        short_exits = np.zeros(n, dtype=np.bool_)

        pos = 0
        isLong = False
        trailStop = np.nan

        for i in range(20, n):
            if np.isnan(ma_val[i-1]) or np.isnan(ma_val[i-2]):
                continue

            longEntry = (close_p[i-1] > ma_val[i-1]) and (close_p[i-2] <= ma_val[i-2])
            shortEntry = (close_p[i-1] < ma_val[i-1]) and (close_p[i-2] >= ma_val[i-2])

            triggered_entry = False

            if longEntry:
                if pos == -1:
                    short_exits[i] = True
                entries[i] = True
                pos = 1
                isLong = True
                trailStop = close_p[i-1] - atr_val[i-1] * 2.0
                triggered_entry = True

            elif shortEntry:
                if pos == 1:
                    exits[i] = True
                short_entries[i] = True
                pos = -1
                isLong = False
                trailStop = close_p[i-1] + atr_val[i-1] * 2.0
                triggered_entry = True

            if not triggered_entry:
                if isLong and pos == 1:
                    newStop = close_p[i-1] - atr_val[i-1] * 2.0
                    if not np.isnan(trailStop):
                        trailStop = max(trailStop, newStop)
                    else:
                        trailStop = newStop
                    if close_p[i-1] < trailStop:
                        exits[i] = True
                        pos = 0
                        isLong = False

                elif not isLong and pos == -1:
                    newStop = close_p[i-1] + atr_val[i-1] * 2.0
                    if not np.isnan(trailStop):
                        trailStop = min(trailStop, newStop)
                    else:
                        trailStop = newStop
                    if close_p[i-1] > trailStop:
                        short_exits[i] = True
                        pos = 0

        return entries, short_entries, exits, short_exits

    entries, short_entries, exits, short_exits = atr_stop_loop_nb(high_p, low_p, close_p, open_p)

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
