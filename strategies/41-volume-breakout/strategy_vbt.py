import pandas as pd
import numpy as np
import vectorbt as vbt
from speed.vbt_helpers import atr

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close = df['close']
    open_val = df['open']
    volume = df['volume']

    volMA = volume.rolling(20).mean()
    volSpike = volume > volMA * 1.5
    atr_val = atr(df['high'], df['low'], close, 14)

    priceBreakUp = close > close.shift(1) + atr_val * 1.0
    priceBreakDown = close < close.shift(1) - atr_val * 1.0

    entries = priceBreakUp & volSpike
    short_entries = priceBreakDown & volSpike

    exits = (close < close.shift(1)) & (volume < volMA)
    short_exits = (close > close.shift(1)) & (volume < volMA)

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
