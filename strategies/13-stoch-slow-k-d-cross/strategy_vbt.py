import pandas as pd
import vectorbt as vbt
from speed.vbt_helpers import stoch

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close = df['close']
    open_val = df['open']
    raw_k = stoch(close, df['high'], df['low'], 14)
    slow_k = raw_k.rolling(3).mean()
    slow_d = slow_k.rolling(3).mean()

    entries = (slow_k > slow_d) & (slow_k.shift(1) <= slow_d.shift(1)) & (slow_k < 80)
    short_entries = (slow_k < slow_d) & (slow_k.shift(1) >= slow_d.shift(1)) & (slow_k > 20)

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
