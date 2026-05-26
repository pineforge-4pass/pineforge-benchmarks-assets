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
    if 'timestamp' in df.columns:
        dt = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
    else:
        dt = pd.to_datetime(df.index, utc=True)

    hours = dt.dt.hour.values
    minutes = dt.dt.minute.values
    # Pine dayofweek mapping (Sunday=1, Monday=2...)
    pine_dows = ((dt.dt.dayofweek.values + 1) % 7) + 1

    n = len(df)

    # In this strategy, process_orders_on_close = true.
    # Therefore, close orders (like strategy.close) execute at the close of the bar on which they are called.
    # Entry orders (strategy.entry) with a stop price still execute on the NEXT bar if the stop triggers.
    # Wait, the comment says: "so the strategy.close market exit fires on the SAME bar as the cross event (at that bar's close),
    # while the stop entry still waits for the NEXT bar's open."
    # So if on bar i, hour==8 and minute==0 (isDown):
    # - close("LE") is executed immediately at the close of bar i (so fill price is close_p[i], index of exit is i)
    # - entry("SE") with high*10 stop is evaluated, triggers on bar i+1 and fills at open_p[i+1] (index of entry is i+1).
    # This is a key difference from strategy 51!

    @njit
    def logic_loop(close_p, open_p, high_p, low_p, hours, minutes, pine_dows):
        entries = np.zeros(n, dtype=np.bool_)
        short_entries = np.zeros(n, dtype=np.bool_)
        exits = np.zeros(n, dtype=np.bool_)
        short_exits = np.zeros(n, dtype=np.bool_)

        # Since vectorbt from_signals expects execution at the same price array (usually open),
        # but here we have some fills at close (index i) and some at open (index i+1),
        # how can we handle different fill prices?
        # If we specify `price` as a Series/array, can we have different prices for entries and exits?
        # Yes! Vectorbt's from_signals accepts price as a Series/array. But the entry and exit are filled at whatever
        # value the price array has at that index.
        # If we want entry to fill at open_p[i] and exit to fill at close_p[i], we can customize the price array!
        # Wait, if we use a custom price array, let's see. If entries and exits occur on different bars,
        # we can just construct a `custom_price` array where for each bar, if it's an entry bar we set it to open_p,
        # and if it's an exit bar we set it to close_p.
        # Let's write the loop to find entries and exits:

        pos = 0 # 1 for long, -1 for short, 0 for flat
        custom_price = np.copy(open_p)

        for i in range(0, n - 1):
            isDown = (hours[i] == 8) and (minutes[i] == 0)
            isUp = (hours[i] == 14) and (minutes[i] == 0)
            isReset = (pine_dows[i] == 2) and (hours[i] == 0) and (minutes[i] == 0)

            # process_orders_on_close = true
            # Market close orders (strategy.close) execute at the close of bar i
            if isDown:
                if pos == 1:
                    exits[i] = True
                    custom_price[i] = close_p[i]
                    pos = 0
                # Stop entry SE with stop high*10 fills at next bar open (i+1)
                short_entries[i+1] = True
                custom_price[i+1] = open_p[i+1]
                pos = -1

            elif isUp:
                if pos == -1:
                    short_exits[i] = True
                    custom_price[i] = close_p[i]
                    pos = 0
                # Stop entry LE with stop low*0.1 fills at next bar open (i+1)
                entries[i+1] = True
                custom_price[i+1] = open_p[i+1]
                pos = 1

            elif isReset and pos != 0:
                if pos == 1:
                    exits[i] = True
                    custom_price[i] = close_p[i]
                else:
                    short_exits[i] = True
                    custom_price[i] = close_p[i]
                pos = 0

        return entries, short_entries, exits, short_exits, custom_price

    entries, short_entries, exits, short_exits, custom_price = logic_loop(close_p, open_p, high_p, low_p, hours, minutes, pine_dows)

    return vbt.Portfolio.from_signals(
        df['close'],
        entries=pd.Series(entries, index=df.index),
        short_entries=pd.Series(short_entries, index=df.index),
        exits=pd.Series(exits, index=df.index),
        short_exits=pd.Series(short_exits, index=df.index),
        price=pd.Series(custom_price, index=df.index),
        init_cash=1000000,
        fees=fees,
        slippage=0.0,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
