import pandas as pd
import vectorbt as vbt

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close = df['close']
    open_val = df['open']

    ma1 = close.rolling(10).mean()
    ma2 = close.rolling(20).mean()
    ma3 = close.rolling(50).mean()

    bullStack = (ma1 > ma2) & (ma2 > ma3)
    bearStack = (ma1 < ma2) & (ma2 < ma3)

    entries = bullStack & ~bullStack.shift(1).fillna(False)
    short_entries = bearStack & ~bearStack.shift(1).fillna(False)

    exits = ~bullStack
    short_exits = ~bearStack

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
