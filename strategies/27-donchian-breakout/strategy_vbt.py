import pandas as pd
import vectorbt as vbt

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close = df['close']
    high_p = df['high']
    low_p = df['low']
    open_val = df['open']

    entryUpper = high_p.rolling(20).max()
    entryLower = low_p.rolling(20).min()

    exitUpper = high_p.rolling(10).max()
    exitLower = low_p.rolling(10).min()

    entries = close > entryUpper.shift(1)
    short_entries = close < entryLower.shift(1)

    exits = close < exitLower.shift(1)
    short_exits = close > exitUpper.shift(1)

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
