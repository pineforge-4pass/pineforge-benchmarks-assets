import pandas as pd
import vectorbt as vbt
from speed.vbt_helpers import rsi

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close = df['close']
    open_val = df['open']

    bbMid = close.rolling(20).mean()
    bbDev = close.rolling(20).std(ddof=0)
    bbUpper = bbMid + 2.0 * bbDev
    bbLower = bbMid - 2.0 * bbDev

    rsi_val = rsi(close, 14)

    entries = (close < bbLower) & (rsi_val < 30)
    short_entries = (close > bbUpper) & (rsi_val > 70)

    exits = close > bbMid
    short_exits = close < bbMid

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
