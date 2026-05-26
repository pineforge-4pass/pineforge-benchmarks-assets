import pandas as pd
import numpy as np
import vectorbt as vbt
from speed.vbt_helpers import ema_ribbon_transitions

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close = df['close']
    open_val = df['open']

    emaFast = close.ewm(span=8, adjust=False).mean()
    emaMid = close.ewm(span=21, adjust=False).mean()
    emaSlow = close.ewm(span=55, adjust=False).mean()

    bullStack = (emaFast > emaMid) & (emaMid > emaSlow)
    bearStack = (emaFast < emaMid) & (emaMid < emaSlow)

    entries_nb, short_entries_nb = ema_ribbon_transitions(
        bullStack.values.astype(np.bool_),
        bearStack.values.astype(np.bool_)
    )
    entries = pd.Series(entries_nb, index=close.index)
    short_entries = pd.Series(short_entries_nb, index=close.index)

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
