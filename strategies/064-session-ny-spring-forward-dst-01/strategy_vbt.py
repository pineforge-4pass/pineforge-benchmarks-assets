import pandas as pd
import vectorbt as vbt

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    # Convert timestamps to New York timezone
    ny_time = pd.to_datetime(df['timestamp'], unit='ms').dt.tz_localize('UTC').dt.tz_convert('America/New_York')
    time_num = ny_time.dt.hour * 100 + ny_time.dt.minute

    inSess = (time_num >= 930) & (time_num < 1600)
    wasInSess = inSess.shift(1).fillna(False)

    entries = inSess & (~wasInSess)
    exits = wasInSess & (~inSess)

    return vbt.Portfolio.from_signals(
        df['close'],
        entries=entries.shift(1).fillna(False),
        exits=exits.shift(1).fillna(False),
        price=df['open'],
        init_cash=1000000,
        fees=fees,
        slippage=0.0,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
