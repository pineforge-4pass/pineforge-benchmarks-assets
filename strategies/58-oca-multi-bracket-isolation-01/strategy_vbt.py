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

    # Pre-computations
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
    def ema_nb(arr, length):
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
        alpha = 2.0 / (length + 1)
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
    emaFast = ema_nb(close_p, 9)
    emaSlow = ema_nb(close_p, 21)

    @njit
    def logic_loop(close_p, open_p, high_p, low_p, rsiVal, atrVal, emaFast, emaSlow):
        entries = np.zeros(n, dtype=np.bool_)
        short_entries = np.zeros(n, dtype=np.bool_)
        exits = np.zeros(n, dtype=np.bool_)
        short_exits = np.zeros(n, dtype=np.bool_)

        # To support partial exits with vectorbt from_signals, we need to carefully track position size.
        # But wait, vbt.Portfolio.from_signals can use size/size_type. However, size is usually a single array or scalar.
        # Since we have two separate independent brackets (A and B), we can model the portfolio by treating
        # each bracket exit as an exit signal.
        # Or, we can specify a custom size array for entries and exits.
        # Wait, if we use entries and exits with custom size, we can specify:
        # entries_size = np.zeros(n)
        # exits_size = np.zeros(n)
        # This is very flexible!
        # Let's see: vbt.Portfolio.from_signals size parameter can be a Series or array.
        # If we specify `size` as an array representing the order sizes (e.g. qty=2 for entries, qty=1 for exits),
        # we can do that!
        # Let's verify how size is handled:
        # "upon_opposite_entry='reverse'"
        # If size_type is 'Amount', size specifies the target amount or execution amount?
        # In vbt, if size_type='Amount', size represents the cash/quantity amount.
        # Let's write the logic loop that computes `entries`, `exits`, and `size`.
        # To keep it simple and compile with @njit, we can track position size manually:
        pos = 0 # Can be 0, 1, or 2 (representing position of 0, 1, or 2 contracts)
        entry_price = 0.0

        # Brackets
        limit_a = np.nan
        stop_a = np.nan
        limit_b = np.nan
        stop_b = np.nan

        bracket_a_active = False
        bracket_b_active = False

        # We will record trade sizes:
        # entries: True on entry
        # exits: True when a bracket exits (or closes)
        # We need to construct custom signal arrays for entries and exits.
        # If we exit qty 1, we can trigger an exit. If both exit, we trigger exits.
        # Wait! Vectorbt's accumulate=False by default.
        # If we enter with qty=2, and exit with qty=1 twice, can we do it?
        # Let's see: in vectorbt, if entries has True and exits has True, but we want to scale out,
        # we can use `accumulate=True` or `size` array.
        # Let's look at another way: since it is a long-only strategy with qty=2, can we split the portfolio into two independent sub-portfolios of qty=1 each?
        # Sub-portfolio A: qty=1, entered on crossover, exited via bracket A (atr * 1.0)
        # Sub-portfolio B: qty=1, entered on crossover, exited via bracket B (atr * 2.0)
        # That is mathematically EXACTLY identical to a single portfolio with qty=2 and partial exits!
        # Because the brackets are independent, and there's no pyramiding, they do not interact.
        # Split-portfolio approach is extremely elegant, robust, and 100% correct in vectorbt without complex sizing!
        # Let's implement this!

        # Sub-portfolio A:
        entries_A = np.zeros(n, dtype=np.bool_)
        exits_A = np.zeros(n, dtype=np.bool_)
        pos_A = 0
        limit_A = np.nan
        stop_A = np.nan

        for i in range(1, n):
            prev_idx = i - 1
            if np.isnan(rsiVal[prev_idx]) or np.isnan(emaFast[prev_idx]) or np.isnan(emaSlow[prev_idx]):
                continue

            crossover = (emaFast[prev_idx] > emaSlow[prev_idx]) and (emaFast[prev_idx-1] <= emaSlow[prev_idx-1])
            entryCond = crossover and (rsiVal[prev_idx] < 60.0)

            if pos_A == 1:
                if low_p[i] <= stop_A:
                    exits_A[i] = True
                    pos_A = 0
                elif high_p[i] >= limit_A:
                    exits_A[i] = True
                    pos_A = 0

            if pos_A == 0 and entryCond:
                entries_A[i] = True
                pos_A = 1
                entry_price = open_p[i]
                limit_A = entry_price + atrVal[prev_idx] * 1.0
                stop_A = entry_price - atrVal[prev_idx] * 1.0

        # Sub-portfolio B:
        entries_B = np.zeros(n, dtype=np.bool_)
        exits_B = np.zeros(n, dtype=np.bool_)
        pos_B = 0
        limit_B = np.nan
        stop_B = np.nan

        for i in range(1, n):
            prev_idx = i - 1
            if np.isnan(rsiVal[prev_idx]) or np.isnan(emaFast[prev_idx]) or np.isnan(emaSlow[prev_idx]):
                continue

            crossover = (emaFast[prev_idx] > emaSlow[prev_idx]) and (emaFast[prev_idx-1] <= emaSlow[prev_idx-1])
            entryCond = crossover and (rsiVal[prev_idx] < 60.0)

            if pos_B == 1:
                if low_p[i] <= stop_B:
                    exits_B[i] = True
                    pos_B = 0
                elif high_p[i] >= limit_B:
                    exits_B[i] = True
                    pos_B = 0

            if pos_B == 0 and entryCond:
                entries_B[i] = True
                pos_B = 1
                entry_price = open_p[i]
                limit_B = entry_price + atrVal[prev_idx] * 2.0
                stop_B = entry_price - atrVal[prev_idx] * 2.0

        return entries_A, exits_A, entries_B, exits_B

    entries_A, exits_A, entries_B, exits_B = logic_loop(close_p, open_p, high_p, low_p, rsiVal, atrVal, emaFast, emaSlow)

    # Let's combine the two sub-portfolios or combine signals:
    # Actually, we can just run two portfolios and sum their trades, but we need to return a single vbt.Portfolio!
    # In vectorbt, we can pass 2D columns or multiple columns of signals to run both at once.
    # Passing a 2D DataFrame/numpy array of entries and exits will run multiple column columns, and return a single Portfolio object!
    # Let's do that!
    entries_df = pd.DataFrame({
        'A': entries_A,
        'B': entries_B
    }, index=df.index)

    exits_df = pd.DataFrame({
        'A': exits_A,
        'B': exits_B
    }, index=df.index)

    # We return the combined portfolio
    return vbt.Portfolio.from_signals(
        df['close'],
        entries=entries_df,
        exits=exits_df,
        price=df['open'],
        init_cash=500000, # 500k each to total 1M capital
        fees=fees,
        slippage=0.0,
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
