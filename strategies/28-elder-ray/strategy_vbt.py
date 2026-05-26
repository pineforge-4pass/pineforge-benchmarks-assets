import pandas as pd
import vectorbt as vbt

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close = df['close']
    high_p = df['high']
    low_p = df['low']
    open_val = df['open']

    ema_val = close.ewm(span=13, adjust=False).mean()
    bullPower = high_p - ema_val
    bearPower = low_p - ema_val

    emaTrend = close.ewm(span=50, adjust=False).mean()
    upTrend = close > emaTrend
    dnTrend = close < emaTrend

    entries = upTrend & (bearPower < 0) & (bearPower > bearPower.shift(1))
    short_entries = dnTrend & (bullPower > 0) & (bullPower < bullPower.shift(1))

    exits = (bearPower > 0) & (bearPower < bearPower.shift(1))
    short_exits = (bullPower < 0) & (bullPower > bullPower.shift(1))

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
