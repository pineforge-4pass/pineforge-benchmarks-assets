import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close_p = df['close'].values
    high_p = df['high'].values
    low_p = df['low'].values
    open_p = df['open'].values
    n = len(df)

    # Standard rsi & atr functions
    @njit
    def rma_nb(arr, length):
        out = np.empty(len(arr))
        out[:] = np.nan
        first_idx = 0
        while first_idx < len(arr) and np.isnan(arr[first_idx]):
            first_idx += 1
        if len(arr) - first_idx < length:
            return out
        sma_init = 0.0
        for i in range(first_idx, first_idx + length):
            sma_init += arr[i]
        sma_init /= length
        out[first_idx + length - 1] = sma_init
        alpha = 1.0 / length
        for i in range(first_idx + length, len(arr)):
            out[i] = alpha * arr[i] + (1 - alpha) * out[i-1]
        return out

    @njit
    def rsi_nb(close, length):
        out = np.empty(len(close))
        out[:] = np.nan
        if len(close) < length + 1:
            return out
        deltas = np.empty(len(close))
        deltas[0] = 0.0
        for i in range(1, len(close)):
            deltas[i] = close[i] - close[i-1]

        gains = np.where(deltas > 0, deltas, 0.0)
        losses = np.where(deltas < 0, -deltas, 0.0)

        avg_gains = rma_nb(gains, length)
        avg_losses = rma_nb(losses, length)

        for i in range(len(close)):
            if np.isnan(avg_gains[i]) or np.isnan(avg_losses[i]):
                continue
            if avg_losses[i] == 0:
                out[i] = 100.0
            else:
                rs = avg_gains[i] / avg_losses[i]
                out[i] = 100.0 - (100.0 / (1.0 + rs))
        return out

    @njit
    def tr_nb(high, low, close):
        out = np.empty(len(close))
        out[0] = high[0] - low[0]
        for i in range(1, len(close)):
            out[i] = max(high[i] - low[i], abs(high[i] - close[i-1]), abs(low[i] - close[i-1]))
        return out

    @njit
    def atr_nb(high, low, close, length):
        tr = tr_nb(high, low, close)
        return rma_nb(tr, length)

    rsiVal = rsi_nb(close_p, 14)
    atrVal = atr_nb(high_p, low_p, close_p, 14)

    @njit
    def logic_loop(close_p, open_p, high_p, low_p, rsiVal, atrVal):
        entries = np.zeros(n, dtype=np.bool_)
        short_entries = np.zeros(n, dtype=np.bool_)
        exits = np.zeros(n, dtype=np.bool_)
        short_exits = np.zeros(n, dtype=np.bool_)

        pos = 0 # 1 for long, 0 for flat
        entry_price = 0.0
        limit_price = np.nan
        stop_price = np.nan

        for i in range(1, n):
            prev_idx = i - 1
            if np.isnan(rsiVal[prev_idx]) or np.isnan(rsiVal[prev_idx-1]):
                continue

            # Standard crossover: rsiVal crossed over 30
            crossover = (rsiVal[prev_idx] > 30.0) and (rsiVal[prev_idx-1] <= 30.0)

            # Check if active position is hit by bracket SL/TP
            if pos == 1:
                # We need to simulate the intra-bar bracket hit
                # In Pine, TP limit and SL stop orders are checked on bar i.
                # If high >= limit_price and low <= stop_price, we look at which was hit first or just fill one.
                # Usually standard backtest: check stop first (pessimistic) or check which is closer to open.
                # Let's check stop first:
                if low_p[i] <= stop_price:
                    exits[i] = True
                    pos = 0
                elif high_p[i] >= limit_price:
                    exits[i] = True
                    pos = 0

            # If we are flat, we can enter long on crossover
            if pos == 0 and crossover:
                entries[i] = True
                pos = 1
                # The execution is on bar i open
                entry_price = open_p[i]
                limit_price = entry_price + atrVal[prev_idx] * 1.5
                stop_price = entry_price - atrVal[prev_idx] * 1.5

        return entries, short_entries, exits, short_exits

    entries, short_entries, exits, short_exits = logic_loop(close_p, open_p, high_p, low_p, rsiVal, atrVal)

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
