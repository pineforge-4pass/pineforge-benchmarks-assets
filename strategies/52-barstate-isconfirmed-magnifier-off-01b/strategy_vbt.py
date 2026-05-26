import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    # Let's extract the parameters and compute EMA 9 and 21
    # We can use pandas to compute EMAs or njit
    close_p = df['close'].values
    open_p = df['open'].values
    n = len(df)

    # EMA calculation
    # Pine ta.ema has alpha = 2 / (length + 1)
    # So length=9 -> alpha=2/10 = 0.2. length=21 -> alpha=2/22 = 1/11
    # Let's write standard EMA calculation inside @njit to make it super fast and accurate.
    @njit
    def compute_ema(arr, length):
        out = np.empty(len(arr))
        out[:] = np.nan
        if len(arr) < length:
            return out
        # Pine ta.ema uses SMA for the first value, or just initializes on the first available.
        # Actually standard Pine ema: first value is SMA of the first length bars.
        sma_init = 0.0
        for i in range(length):
            sma_init += arr[i]
        sma_init /= length
        out[length-1] = sma_init
        alpha = 2.0 / (length + 1)
        for i in range(length, len(arr)):
            out[i] = alpha * arr[i] + (1 - alpha) * out[i-1]
        return out

    ema9 = compute_ema(close_p, 9)
    ema21 = compute_ema(close_p, 21)

    @njit
    def logic_loop(close_p, open_p, ema9, ema21):
        entries = np.zeros(n, dtype=np.bool_)
        short_entries = np.zeros(n, dtype=np.bool_)
        exits = np.zeros(n, dtype=np.bool_)
        short_exits = np.zeros(n, dtype=np.bool_)

        pendingLong = False
        pendingExit = False
        pos = 0 # 1 for long, 0 for flat

        for i in range(1, n):
            # Crossover and crossunder conditions on bar i-1 (historical lookup)
            # Pine crossover: ema9[i-1] > ema21[i-1] and ema9[i-2] <= ema21[i-2]
            if np.isnan(ema9[i-1]) or np.isnan(ema21[i-1]) or np.isnan(ema9[i-2]) or np.isnan(ema21[i-2]):
                continue

            crossover = (ema9[i-1] > ema21[i-1]) and (ema9[i-2] <= ema21[i-2])
            crossunder = (ema9[i-1] < ema21[i-1]) and (ema9[i-2] >= ema21[i-2])

            if crossover:
                pendingLong = True
            if crossunder:
                pendingExit = True

            # "barstate.isconfirmed" is always True for historical bars on bar close.
            # So inside standard OHLC historical backtest, barstate.isconfirmed is True for every bar we iterate.
            # The execution of the strategy happens at the close of bar i-1, meaning orders execute on open of bar i.
            # Let's align carefully.
            # In Pine:
            # if barstate.isconfirmed and pendingLong and strategy.position_size == 0
            #     strategy.entry("L", strategy.long)
            #     pendingLong := false
            # This order is sent on bar i-1 close, executing on bar i open.
            # Let's check:
            if pendingLong and pos == 0:
                entries[i] = True
                pos = 1
                pendingLong = False

            if pendingExit and pos > 0:
                exits[i] = True
                pos = 0
                pendingExit = False

        return entries, short_entries, exits, short_exits

    entries, short_entries, exits, short_exits = logic_loop(close_p, open_p, ema9, ema21)

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
