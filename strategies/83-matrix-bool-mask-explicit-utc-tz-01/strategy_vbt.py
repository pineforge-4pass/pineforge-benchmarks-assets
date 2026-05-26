import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit
from speed.vbt_helpers import rsi

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    # Ensure UTC timezone
    if 'timestamp' in df.columns:
        dt = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
        hours = dt.dt.hour.values
        days = ((dt.dt.dayofweek + 1) % 7).values
    else:
        dt = pd.to_datetime(df.index, utc=True)
        hours = dt.hour.values
        days = ((dt.dayofweek + 1) % 7).values

    close = df['close']
    rsi_val = rsi(close, 14)
    rsi_values = rsi_val.values

    n = len(df)

    @njit
    def run_loop(hours, days, rsi_values):
        entry_signals = np.zeros(n, dtype=np.bool_)
        exit_signals = np.zeros(n, dtype=np.bool_)

        mask = np.zeros((24, 7), dtype=np.bool_)

        for i in range(n):
            rsiVal = rsi_values[i]
            h = hours[i]
            d = days[i]

            if not np.isnan(rsiVal) and rsiVal > 60.0 and 0 <= h < 24 and 0 <= d < 7:
                mask[h, d] = True

            sample = mask[h, d] if (0 <= h < 24 and 0 <= d < 7) else False

            hotCount = 0
            for r in range(24):
                for c in range(7):
                    if mask[r, c]:
                        hotCount += 1

            entry_signals[i] = (hotCount >= 6) and (rsiVal > 55.0) and sample
            exit_signals[i] = not np.isnan(rsiVal) and (rsiVal < 45.0)

        return entry_signals, exit_signals

    entry_signals, exit_signals = run_loop(hours, days, rsi_values)

    entries = pd.Series(entry_signals, index=df.index).shift(1).fillna(False)
    exits = pd.Series(exit_signals, index=df.index).shift(1).fillna(False)

    return vbt.Portfolio.from_signals(
        close,
        entries=entries,
        exits=exits,
        price=df['open'],
        fees=fees,
        init_cash=1000000,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
