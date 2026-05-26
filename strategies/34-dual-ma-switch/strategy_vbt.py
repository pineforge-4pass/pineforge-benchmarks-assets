import pandas as pd
import vectorbt as vbt

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close = df['close']
    open_val = df['open']

    fast_ma = close.ewm(span=10, adjust=False).mean()
    slow_ma = close.ewm(span=30, adjust=False).mean()

    entries = (fast_ma > slow_ma) & (fast_ma.shift(1) <= slow_ma.shift(1))
    short_entries = (fast_ma < slow_ma) & (fast_ma.shift(1) >= slow_ma.shift(1))

    return vbt.Portfolio.from_signals(
        close,
        entries=entries.shift(1).fillna(False),
        short_entries=short_entries.shift(1).fillna(False),
        price=open_val,
        init_cash=1000000,
        fees=fees,
        slippage=0.0,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
