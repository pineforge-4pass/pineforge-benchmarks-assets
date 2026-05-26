import pandas as pd
import vectorbt as vbt
from speed.vbt_helpers import vwma

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close = df['close']
    open_val = df['open']

    vwma_val = vwma(close, df['volume'], 20)
    sma_val = close.rolling(20).mean()
    vwma_diff = vwma_val - sma_val

    entries = (vwma_diff > 0) & (vwma_diff.shift(1) <= 0)
    short_entries = (vwma_diff < 0) & (vwma_diff.shift(1) >= 0)

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
