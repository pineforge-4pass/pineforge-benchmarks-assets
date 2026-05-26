import pandas as pd
import numpy as np
import vectorbt as vbt

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    dts = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
    hours = dts.dt.hour.values
    minutes = dts.dt.minute.values
    days = dts.dt.date.values

    n = len(df)
    entries = np.zeros(n, dtype=np.bool_)
    short_entries = np.zeros(n, dtype=np.bool_)
    exits = np.zeros(n, dtype=np.bool_)
    short_exits = np.zeros(n, dtype=np.bool_)

    pos = 0
    filled_today = 0
    last_day = None
    intraday_cap_hit = False

    for i in range(n - 1):
        day = days[i]
        if day != last_day:
            last_day = day
            filled_today = 0
            intraday_cap_hit = False

        if hours[i] == 0 and minutes[i] == 15:
            if not intraday_cap_hit and pos < 2:
                entries[i+1] = True
                filled_today += 1
                pos += 1
                if filled_today >= 3:
                    intraday_cap_hit = True

        elif hours[i] == 0 and minutes[i] == 30:
            if not intraday_cap_hit and pos < 2:
                entries[i+1] = True
                filled_today += 1
                pos += 1
                if filled_today >= 3:
                    intraday_cap_hit = True

        elif hours[i] == 0 and minutes[i] == 45:
            if not intraday_cap_hit and pos < 2:
                entries[i+1] = True
                filled_today += 1
                pos += 1
                if filled_today >= 3:
                    intraday_cap_hit = True

        elif hours[i] == 1 and minutes[i] == 0:
            if not intraday_cap_hit and pos > 0:
                exits[i+1] = True
                filled_today += 1
                pos = 0
                if filled_today >= 3:
                    intraday_cap_hit = True

        elif hours[i] == 3 and minutes[i] == 0:
            if not intraday_cap_hit and pos > 0:
                exits[i+1] = True
                filled_today += 1
                pos = 0
                if filled_today >= 3:
                    intraday_cap_hit = True

    return vbt.Portfolio.from_signals(
        df['close'],
        entries=pd.Series(entries, index=df.index),
        short_entries=pd.Series(short_entries, index=df.index),
        exits=pd.Series(exits, index=df.index),
        short_exits=pd.Series(short_exits, index=df.index),
        price=df['open'],
        init_cash=1000000,
        fees=fees,
        slippage=0.0,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
