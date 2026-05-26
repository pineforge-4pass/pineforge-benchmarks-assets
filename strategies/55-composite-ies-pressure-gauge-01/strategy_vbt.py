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

    # Parameters
    i_pressure_len = 14
    i_pressure_smooth = 5
    i_pressure_mom = 10
    i_pressure_high = 0.7
    i_pressure_low = 0.3
    i_pressure_thresh = 0.05

    # raw_buy calculation
    bar_range = high_p - low_p
    raw_buy = np.empty(n)
    for i in range(n):
        raw_buy[i] = (close_p[i] - low_p[i]) / bar_range[i] if bar_range[i] > 0 else 0.5

    pressure_ratio = ema_nb(raw_buy, i_pressure_len)
    pressure_smooth = ema_nb(pressure_ratio, i_pressure_smooth)

    @njit
    def logic_loop(close_p, open_p, pressure_smooth):
        entries = np.zeros(n, dtype=np.bool_)
        short_entries = np.zeros(n, dtype=np.bool_)
        exits = np.zeros(n, dtype=np.bool_)
        short_exits = np.zeros(n, dtype=np.bool_)

        pressure_bull_arr = np.zeros(n, dtype=np.bool_)
        pressure_bear_arr = np.zeros(n, dtype=np.bool_)

        for i in range(n):
            if np.isnan(pressure_smooth[i]) or (i - i_pressure_mom < 0):
                continue
            press_s = pressure_smooth[i]
            press_mom = press_s - pressure_smooth[i - i_pressure_mom]

            pressure_state = 0
            if press_s >= i_pressure_high:
                pressure_state = 2
            elif press_s > 0.5 + i_pressure_thresh:
                pressure_state = 1
            elif press_s <= i_pressure_low:
                pressure_state = -2
            elif press_s < 0.5 - i_pressure_thresh:
                pressure_state = -1

            pressure_bull_arr[i] = (pressure_state >= 1) or (press_mom > i_pressure_thresh)
            pressure_bear_arr[i] = (pressure_state <= -1) or (press_mom < -i_pressure_thresh)

        pos = 0 # 1 for long, -1 for short, 0 for flat

        for i in range(1, n):
            prev_idx = i - 1
            if prev_idx - 1 < 0:
                continue

            pb = pressure_bull_arr[prev_idx]
            pb_prev = pressure_bull_arr[prev_idx - 1]

            ps = pressure_bear_arr[prev_idx]
            ps_prev = pressure_bear_arr[prev_idx - 1]

            long_entry = pb and (not pb_prev) and (pos <= 0)
            short_entry = ps and (not ps_prev) and (pos >= 0)

            if long_entry:
                if pos == -1:
                    short_exits[i] = True
                entries[i] = True
                pos = 1
            elif short_entry:
                if pos == 1:
                    exits[i] = True
                short_entries[i] = True
                pos = -1

        return entries, short_entries, exits, short_exits

    entries, short_entries, exits, short_exits = logic_loop(close_p, open_p, pressure_smooth)

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
