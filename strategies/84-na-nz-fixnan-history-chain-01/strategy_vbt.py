import pandas as pd
import numpy as np
import vectorbt as vbt

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close = df['close']
    open_val = df['open']

    raw_delta = close.diff(1)
    safe_delta = raw_delta.fillna(0.0)
    held_delta = raw_delta.ffill()

    combined = safe_delta + held_delta.fillna(0.0)
    score = combined.rolling(8).mean()

    score_prev = score.shift(1).fillna(0.0)

    long_signal = score.notna() & (score > 0.0) & (score_prev <= 0.0)
    flat_signal = score.notna() & (score < 0.0) & (score_prev >= 0.0)

    entries = long_signal.shift(1).fillna(False)
    exits = flat_signal.shift(1).fillna(False)

    return vbt.Portfolio.from_signals(
        close,
        entries=entries,
        exits=exits,
        price=open_val,
        fees=fees,
        init_cash=1000000,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
