import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    # Get arrays of OHLC and datetime/hour/minute
    close_p = df['close'].values
    open_p = df['open'].values
    high_p = df['high'].values
    low_p = df['low'].values

    # We need hour, minute, dayofweek
    # Since df usually has a timestamp or datetime column, let's extract them.
    # Note: df usually has 'timestamp' in ms, or datetime.
    if 'timestamp' in df.columns:
        dt = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
    else:
        dt = pd.to_datetime(df.index, utc=True)

    hours = dt.dt.hour.values
    minutes = dt.dt.minute.values
    dayofweeks = dt.dt.dayofweek.values + 1 # Pine dayofweek: Sunday=1, Monday=2, ..., Saturday=7
    # Note: pandas dayofweek has Monday=0, Tuesday=1... Sunday=6.
    # Let's map pandas dayofweek to Pine dayofweek:
    # pandas: 0 (Mon), 1 (Tue), 2 (Wed), 3 (Thu), 4 (Fri), 5 (Sat), 6 (Sun)
    # Pine: 2 (Mon), 3 (Tue), 4 (Wed), 5 (Thu), 6 (Fri), 7 (Sat), 1 (Sun)
    # So Pine = ((pandas + 1) % 7) + 1. Let's verify:
    # Mon: (0 + 1) % 7 + 1 = 2
    # Sun: (6 + 1) % 7 + 1 = 1. Yes, this is correct!
    pine_dows = ((dt.dt.dayofweek.values + 1) % 7) + 1

    n = len(df)

    @njit
    def logic_loop(open_p, high_p, low_p, close_p, hours, minutes, pine_dows):
        entries = np.zeros(n, dtype=np.bool_)
        short_entries = np.zeros(n, dtype=np.bool_)
        exits = np.zeros(n, dtype=np.bool_)
        short_exits = np.zeros(n, dtype=np.bool_)

        pos = 0 # 1 for long, -1 for short, 0 for flat

        for i in range(1, n):
            # Previous bar values
            h_prev = high_p[i-1]
            l_prev = low_p[i-1]
            c_prev = close_p[i-1]

            # Conditions are based on CURRENT bar's hour/minute (which corresponds to execution at next bar's open)
            # In Pine, if isDown evaluates to true on bar i, strategy.entry is called.
            # With process_orders_on_close = false, the order is evaluated on bar i (after close) and executed on bar i+1.
            # The stop order has a limit/stop price.
            # LE stop price is low_p[i] * 0.1. It is guaranteed to fill at open_p[i+1].
            # SE stop price is high_p[i] * 10.0. It is guaranteed to fill at open_p[i+1].

            # Since the conditions are evaluated on bar i (after its close), we check hour/minute of bar i.
            isDown = (hours[i] == 8) and (minutes[i] == 0)
            isUp = (hours[i] == 14) and (minutes[i] == 0)

            # We also check if we close_all on Monday 00:00 (dayofweek == 2, hour == 0, minute == 0)
            isReset = (pine_dows[i] == 2) and (hours[i] == 0) and (minutes[i] == 0)

            # Order evaluation on bar i:
            # If isDown is True on bar i:
            #   We entry strategy.short (SE) with stop=high_p[i]*10.0. This stop is guaranteed to trigger on bar i+1, filling at open_p[i+1].
            #   And cancel LE.
            #   And if pos == 1 (long position from LE), we close LE. This close is on close of bar i or open of bar i+1?
            #   In Pine: "if isDown and strategy.position_size > 0: strategy.close('LE')".
            #   Since process_orders_on_close = false, strategy.close('LE') is evaluated at bar i close, and executes on bar i+1 open.
            #   So on bar i+1, both the short entry (SE) and long close (LE) will execute at open_p[i+1].
            #   Since SE is a reverse or opposite entry, does it net?
            #   Actually, if we just reverse, entering short of qty 1 when long of qty 1 will make us flat, not short of qty 1.
            #   Wait! "pyramiding = 1". If we are long 1, and we do strategy.entry("SE", strategy.short, qty=1),
            #   since it's opposite, let's see: in Pine, does strategy.entry with opposite direction reverse the position?
            #   In Pine, if pyramiding is active, entry does not automatically reverse unless it's a specific setup,
            #   but wait, here we have strategy.close("LE") which closes the long position, and strategy.entry("SE", strategy.short) which enters short.
            #   So on bar i+1 open, the long is closed (qty 1), and short is entered (qty 1).
            #   So the position changes from +1 to -1. That is a complete reversal.
            #   Similarly for isUp: the short is closed, and long is entered.
            #   If isReset is True: we close_all.

            # Let's map this to vbt entries/exits on bar i+1:
            # If isDown[i]:
            #   If pos == 1:
            #     exits[i+1] = True (closes long)
            #   short_entries[i+1] = True (enters short)
            #   pos = -1
            # If isUp[i]:
            #   If pos == -1:
            #     short_exits[i+1] = True (closes short)
            #   entries[i+1] = True (enters long)
            #   pos = 1
            # If isReset[i] and pos != 0:
            #   If pos == 1:
            #     exits[i+1] = True
            #   else:
            #     short_exits[i+1] = True
            #   pos = 0

            # Note: what if multiple conditions happen on the same bar? (They won't, since hours are 8 and 14 and 0).
            if isDown:
                if pos == 1:
                    exits[i] = True # closes long on bar i, executed at open of i
                short_entries[i] = True # enters short on bar i, executed at open of i
                pos = -1
            elif isUp:
                if pos == -1:
                    short_exits[i] = True # closes short on bar i, executed at open of i
                entries[i] = True # enters long on bar i, executed at open of i
                pos = 1
            elif isReset and pos != 0:
                if pos == 1:
                    exits[i] = True
                else:
                    short_exits[i] = True
                pos = 0

        return entries, short_entries, exits, short_exits

    # Note about indexing:
    # In the loop, the decisions are made on bar i-1 (since isDown etc use the timestamps of the completed bar),
    # but let's see. In Pine:
    # "isDown = hour == 8 and minute == 0"
    # This evaluates to true on the bar whose timestamp has hour 8 and minute 0.
    # On that bar's close, the strategy orders are sent, to be filled on the NEXT bar's open.
    # Therefore, if the bar at index i has hour 8 and minute 0, then the orders are filled at index i+1's open.
    # Let's write the loop accordingly!

    @njit
    def logic_loop_corrected(open_p, high_p, low_p, close_p, hours, minutes, pine_dows):
        entries = np.zeros(n, dtype=np.bool_)
        short_entries = np.zeros(n, dtype=np.bool_)
        exits = np.zeros(n, dtype=np.bool_)
        short_exits = np.zeros(n, dtype=np.bool_)

        pos = 0

        for i in range(0, n - 1):
            isDown = (hours[i] == 8) and (minutes[i] == 0)
            isUp = (hours[i] == 14) and (minutes[i] == 0)
            isReset = (pine_dows[i] == 2) and (hours[i] == 0) and (minutes[i] == 0)

            # Orders are filled on bar i+1
            if isDown:
                if pos == 1:
                    exits[i+1] = True
                short_entries[i+1] = True
                pos = -1
            elif isUp:
                if pos == -1:
                    short_exits[i+1] = True
                entries[i+1] = True
                pos = 1
            elif isReset and pos != 0:
                if pos == 1:
                    exits[i+1] = True
                else:
                    short_exits[i+1] = True
                pos = 0

        return entries, short_entries, exits, short_exits

    entries, short_entries, exits, short_exits = logic_loop_corrected(open_p, high_p, low_p, close_p, hours, minutes, pine_dows)

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
