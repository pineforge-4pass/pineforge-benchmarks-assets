import pandas as pd
import vectorbt as vbt
from speed.vbt_helpers import linreg

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close = df['close']
    open_val = df['open']

    reg_line = linreg(close, 50, 0)
    reg_dev = close.rolling(50).std(ddof=0) * 2.0
    upper_band = reg_line + reg_dev
    lower_band = reg_line - reg_dev

    entries = (close < lower_band) & (close > close.shift(1))
    short_entries = (close > upper_band) & (close < close.shift(1))

    exits = close > reg_line
    short_exits = close < reg_line

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
