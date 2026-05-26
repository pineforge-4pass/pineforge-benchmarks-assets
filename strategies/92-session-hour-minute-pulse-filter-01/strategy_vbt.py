import pandas as pd
import vectorbt as vbt

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    utc_time = pd.to_datetime(df['timestamp'], unit='ms').dt.tz_localize('UTC')
    h = utc_time.dt.hour
    m = utc_time.dt.minute

    entryPulse = (h == 0) & (m == 15)
    exitPulse = (h == 0) & (m == 45)

    return vbt.Portfolio.from_signals(
        df['close'],
        entries=entryPulse.shift(1).fillna(False),
        exits=exitPulse.shift(1).fillna(False),
        price=df['open'],
        init_cash=1000000,
        fees=fees,
        slippage=0.0,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
