import pandas as pd
import vectorbt as vbt
from speed.vbt_helpers import rsi

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close = df['close']
    open_val = df['open']
    rsi_val = rsi(close, 14)
    rsi_signal = rsi_val.ewm(span=9, adjust=False).mean()

    entries = (rsi_val > rsi_signal) & (rsi_val.shift(1) <= rsi_signal.shift(1)) & (rsi_val < 50)
    short_entries = (rsi_val < rsi_signal) & (rsi_val.shift(1) >= rsi_signal.shift(1)) & (rsi_val > 50)

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
