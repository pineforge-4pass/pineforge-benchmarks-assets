import pandas as pd
import vectorbt as vbt
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close = df['close']
    open_val = df['open']

    emaFast = close.ewm(span=9, adjust=False).mean()
    emaSlow = close.ewm(span=21, adjust=False).mean()

    entries = (emaFast > emaSlow) & (emaFast.shift(1) <= emaSlow.shift(1))
    exits = (emaFast < emaSlow) & (emaFast.shift(1) >= emaSlow.shift(1))

    return vbt.Portfolio.from_signals(
        close,
        entries=entries.shift(1).fillna(False),
        short_entries=None,
        exits=exits.shift(1).fillna(False),
        short_exits=None,
        price=open_val,
        init_cash=1000000,
        fees=fees,
        slippage=0.0,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
