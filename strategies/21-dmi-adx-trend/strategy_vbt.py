import pandas as pd
import vectorbt as vbt
from speed.vbt_helpers import dmi

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close = df['close']
    open_val = df['open']
    diplus, diminus, _ = dmi(df['high'], df['low'], close, 14, 14)

    entries = (diplus > diminus) & (diplus.shift(1) <= diminus.shift(1))
    short_entries = (diplus < diminus) & (diplus.shift(1) >= diminus.shift(1))

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
