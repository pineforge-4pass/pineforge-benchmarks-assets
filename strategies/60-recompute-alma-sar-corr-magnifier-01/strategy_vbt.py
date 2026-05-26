import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close_p = df['close'].values
    high_p = df['high'].values
    low_p = df['low'].values
    open_p = df['open'].values
    volume_p = df['volume'].values
    n = len(df)

    # Indicator helpers inside @njit or standalone:
    # 1. ALMA (Arnaud Legoux Moving Average)
    # ALMA formulation:
    # m = offset * (window - 1)
    # s = window / sigma
    # weights = exp(-((i - m)^2) / (2 * s^2))
    # normalised weights so sum = 1
    @njit
    def alma_nb(arr, window=14, offset=0.85, sigma=6.0):
        out = np.empty(len(arr))
        out[:] = np.nan
        if len(arr) < window:
            return out

        m = offset * (window - 1)
        s = window / sigma
        weights = np.empty(window)
        w_sum = 0.0
        for i in range(window):
            w = np.exp(-((i - m) ** 2) / (2.0 * s * s))
            weights[i] = w
            w_sum += w

        for i in range(window):
            weights[i] /= w_sum

        for i in range(window - 1, len(arr)):
            sub = arr[i - window + 1 : i + 1]
            val = 0.0
            for j in range(window):
                val += sub[j] * weights[j]
            out[i] = val
        return out

    # 2. Parabolic SAR
    # ta.sar(start, increment, maximum)
    # start = 0.02, increment = 0.02, maximum = 0.2
    @njit
    def sar_nb(high, low, start=0.02, increment=0.02, maximum=0.2):
        out = np.empty(len(high))
        out[:] = np.nan
        if len(high) < 2:
            return out

        # Initialize SAR
        is_uptrend = True
        sar = low[0]
        ep = high[0]
        af = start

        out[0] = sar

        for i in range(1, len(high)):
            prev_sar = sar
            if is_uptrend:
                sar = prev_sar + af * (ep - prev_sar)
                sar = min(sar, low[i-1], low[max(0, i-2)])
                if high[i] > ep:
                    ep = high[i]
                    af = min(af + increment, maximum)
                if low[i] < sar:
                    is_uptrend = False
                    sar = ep
                    ep = low[i]
                    af = start
            else:
                sar = prev_sar + af * (ep - prev_sar)
                sar = max(sar, high[i-1], high[max(0, i-2)])
                if low[i] < ep:
                    ep = low[i]
                    af = min(af + increment, maximum)
                if high[i] > sar:
                    is_uptrend = True
                    sar = ep
                    ep = high[i]
                    af = start
            out[i] = sar
        return out

    # 3. Rolling Correlation
    # ta.correlation(source1, source2, length)
    @njit
    def correlation_nb(x, y, length=20):
        out = np.empty(len(x))
        out[:] = np.nan
        if len(x) < length:
            return out

        for i in range(length - 1, len(x)):
            sub_x = x[i - length + 1 : i + 1]
            sub_y = y[i - length + 1 : i + 1]

            mean_x = np.mean(sub_x)
            mean_y = np.mean(sub_y)

            num = 0.0
            den_x = 0.0
            den_y = 0.0

            for j in range(length):
                dx = sub_x[j] - mean_x
                dy = sub_y[j] - mean_y
                num += dx * dy
                den_x += dx * dx
                den_y += dy * dy

            if den_x > 0 and den_y > 0:
                out[i] = num / np.sqrt(den_x * den_y)
            else:
                out[i] = 0.0
        return out

    almaVal = alma_nb(close_p, 14, 0.85, 6.0)
    sarVal = sar_nb(high_p, low_p, 0.02, 0.02, 0.2)
    corrVal = correlation_nb(close_p, volume_p, 20)

    @njit
    def logic_loop(close_p, open_p, almaVal, sarVal, corrVal):
        entries = np.zeros(n, dtype=np.bool_)
        short_entries = np.zeros(n, dtype=np.bool_)
        exits = np.zeros(n, dtype=np.bool_)
        short_exits = np.zeros(n, dtype=np.bool_)

        pos = 0 # 1 for long, 0 for flat

        for i in range(1, n):
            prev_idx = i - 1
            if np.isnan(almaVal[prev_idx]) or np.isnan(sarVal[prev_idx]) or np.isnan(corrVal[prev_idx]) or np.isnan(almaVal[prev_idx-1]):
                continue

            # ta.crossover(close, almaVal)
            crossover = (close_p[prev_idx] > almaVal[prev_idx]) and (close_p[prev_idx-1] <= almaVal[prev_idx-1])

            bullEntry = crossover and (sarVal[prev_idx] < close_p[prev_idx]) and (corrVal[prev_idx] > 0.0)
            bearExit = sarVal[prev_idx] > close_p[prev_idx]

            if pos == 1 and bearExit:
                exits[i] = True
                pos = 0

            if pos == 0 and bullEntry:
                entries[i] = True
                pos = 1

        return entries, short_entries, exits, short_exits

    entries, short_entries, exits, short_exits = logic_loop(close_p, open_p, almaVal, sarVal, corrVal)

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
