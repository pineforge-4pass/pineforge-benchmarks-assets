import pandas as pd
import vectorbt as vbt

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close = df['close']
    open_val = df['open']

    mom_val = close - close.shift(10)
    roc_val = (close - close.shift(10)) / close.shift(10) * 100.0

    entries = (mom_val > 0) & (mom_val.shift(1) <= 0) & (roc_val > 0)
    short_entries = (mom_val < 0) & (mom_val.shift(1) >= 0) & (roc_val < 0)

    exits = (mom_val < 0) & (mom_val.shift(1) >= 0)
    short_exits = (mom_val > 0) & (mom_val.shift(1) <= 0)

    return vbt.Portfolio.from_signals(
        close,
        entries=entries.shift(1).fillna(False),
        short_entries=short_entries.shift(1).fillna(False),
        exits=exits.shift(1).fillna(False),
        short_exits=short_exits.shift(1).fillna(False),
        price=open_val,
        init_cash=1000000,
        fees=fees,
        slippage=0.0,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
