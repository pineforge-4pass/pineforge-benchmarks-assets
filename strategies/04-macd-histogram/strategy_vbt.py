import pandas as pd
import vectorbt as vbt

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close = df['close']
    open_val = df['open']

    # MACD calculations using standard EMA (adjust=False matches Pine/ta.ema)
    fast_ema = close.ewm(span=12, adjust=False).mean()
    slow_ema = close.ewm(span=26, adjust=False).mean()
    macdLine = fast_ema - slow_ema
    signalLine = macdLine.ewm(span=9, adjust=False).mean()

    entries = (macdLine > signalLine) & (macdLine.shift(1) <= signalLine.shift(1))
    short_entries = (macdLine < signalLine) & (macdLine.shift(1) >= signalLine.shift(1))

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
