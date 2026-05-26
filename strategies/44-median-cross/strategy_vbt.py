import pandas as pd
import numpy as np
import vectorbt as vbt

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close = df['close']
    open_val = df['open']

    # Parameters from strategy.pine
    medLen = 20
    emaLen = 20

    # Indicators
    medVal = close.rolling(medLen).median()
    emaVal = close.ewm(span=emaLen, adjust=False).mean()

    # Crossover / Crossunder
    longCond = (medVal > emaVal) & (medVal.shift(1) <= emaVal.shift(1))
    shortCond = (medVal < emaVal) & (medVal.shift(1) >= emaVal.shift(1))

    # Shift signals by 1 to execute on the next bar open (process_orders_on_close = false)
    entries = longCond.shift(1).fillna(False)
    short_entries = shortCond.shift(1).fillna(False)

    return vbt.Portfolio.from_signals(
        close,
        entries=entries,
        short_entries=short_entries,
        price=open_val,
        init_cash=1000000,
        fees=fees,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
