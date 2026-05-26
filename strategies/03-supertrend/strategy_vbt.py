import pandas as pd
import vectorbt as vbt
from speed.vbt_helpers import supertrend

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close = df['close']
    open_val = df['open']
    _, in_uptrend = supertrend(df['high'], df['low'], close)

    entries = in_uptrend & (~in_uptrend.shift(1).fillna(False))
    short_entries = (~in_uptrend) & in_uptrend.shift(1).fillna(True)

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
