import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    open_p = df['open'].values
    high_p = df['high'].values
    low_p = df['low'].values
    close_p = df['close'].values
    volume_p = df['volume'].values
    n = len(df)

    # Calculate buyVolume and sellVolume
    buyVolume = np.where(close_p > open_p, volume_p, volume_p * (close_p - low_p) / (high_p - low_p + 0.0001))
    sellVolume = np.where(close_p < open_p, volume_p, volume_p * (high_p - close_p) / (high_p - low_p + 0.0001))
    volumeDelta = buyVolume - sellVolume

    # Rolling sum of volumeDelta over 10 bars
    # Use pandas to easily compute rolling sum
    cumDelta = pd.Series(volumeDelta).rolling(10).sum().fillna(0.0).values

    # Determine crossUp and crossDown signals
    cumDelta_prev = np.empty(n)
    cumDelta_prev[0] = 0.0
    cumDelta_prev[1:] = cumDelta[:-1]

    crossUp = (cumDelta > 0.0) & (cumDelta_prev <= 0.0)
    crossDown = (cumDelta < 0.0) & (cumDelta_prev >= 0.0)

    @njit
    def run_loop(crossUp, crossDown):
        entries = np.zeros(n, dtype=np.bool_)
        exits = np.zeros(n, dtype=np.bool_)

        pos = 0
        for i in range(1, n):
            # Check signals at previous bar (i-1)
            if pos == 1:
                if crossDown[i-1]:
                    exits[i] = True
                    pos = 0

            if pos == 0:
                if crossUp[i-1]:
                    entries[i] = True
                    pos = 1

        return entries, exits

    entries, exits = run_loop(crossUp, crossDown)

    return vbt.Portfolio.from_signals(
        df['close'],
        entries=pd.Series(entries, index=df.index),
        exits=pd.Series(exits, index=df.index),
        price=df['open'],
        fees=fees,
        init_cash=1000000,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
