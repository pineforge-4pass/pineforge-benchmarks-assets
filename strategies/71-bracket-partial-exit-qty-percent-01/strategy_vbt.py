import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close_p = df['close'].values
    high_p = df['high'].values
    low_p = df['low'].values
    open_p = df['open'].values
    n = len(df)

    if 'timestamp' in df.columns:
        dt = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
    else:
        dt = pd.to_datetime(df.index, utc=True)

    hours = dt.dt.hour.values
    minutes = dt.dt.minute.values

    @njit
    def logic_loop(open_p, high_p, low_p, close_p, hours, minutes):
        entries = np.zeros(n, dtype=np.bool_)
        short_entries = np.zeros(n, dtype=np.bool_)
        exits = np.zeros(n, dtype=np.bool_)
        short_exits = np.zeros(n, dtype=np.bool_)

        # To track exact filled executions and support the partial exits
        pos_qty = 0.0
        entry_px = 0.0

        for i in range(1, n):
            # 1. First, handle any intraday exits/stops inside the current bar i
            # On bar i, high_p[i] and low_p[i] can trigger TP limit or SL stop.
            # In Pine, strategy.exit evaluates limit and stop based on previous close's calculations.
            # But the order can only execute on bar i.
            # "HALF_TP" limit price = entry_px * 1.003
            # "REST_SL" stop price = entry_px * 0.994
            # A timeout close "L" can execute at the open of bar i if the condition hour==9 and minute==15 is met on bar i-1.
            # Wait, the timeout condition in Pine:
            # "if strategy.position_size > 0 and hour == 9 and minute == 15: strategy.close('L')"
            # This is evaluated on bar i-1. If true on bar i-1, it closes at the open of bar i.
            # In Pine, "hour" and "minute" refer to the current bar's timestamp.
            # If bar i-1 has hour == 9 and minute == 15, the close order executes on bar i open.

            # Let's check timeout condition from bar i-1:
            timeout_triggered = False
            if pos_qty > 0.0 and hours[i-1] == 9 and minutes[i-1] == 15:
                exits[i] = True
                pos_qty = 0.0
                entry_px = 0.0
                timeout_triggered = True

            # If not timed out at the open, check for bracket fills during bar i:
            if pos_qty > 0.0 and not timeout_triggered:
                tp_px = entry_px * 1.003
                sl_px = entry_px * 0.994

                # Standard TV logic: we look at whether high/low crossed our levels.
                # Since qty_percent = 50, if TP is hit, we exit half position.
                # Remaining position is covered by SL or subsequent bar actions.
                # In Pine, does SL only apply to the REST? Yes, "REST_SL" doesn't have qty_percent so it exits all remaining.
                # If BOTH are hit in the same bar, usually SL is evaluated first or depending on bar direction.
                # But let's check high/low:
                # If we have a full position (qty=2), we can exit half (qty=1).
                # If we have half position (qty=1), we can only exit via SL or timeout (since half tp was already filled).
                # Actually, in Pine:
                # "strategy.exit('HALF_TP', 'L', limit=entry*1.003, qty_percent=50)"
                # "strategy.exit('REST_SL', 'L', stop=entry*0.994)"
                # If we enter with qty 2:
                # Initially pos_qty = 2.0.
                # If high >= tp_px: half is sold. pos_qty becomes 1.0.
                # If low <= sl_px: remaining (or all) is sold.

                # Let's model the intraday fill logic:
                hit_tp = high_p[i] >= tp_px
                hit_sl = low_p[i] <= sl_px

                if hit_tp and hit_sl:
                    # Both hit. If it's a down bar, SL might hit first, or if up bar, TP might hit first.
                    # But normally, let's assume TP hits and then SL hits, or vice-versa.
                    # In this benchmark, let's see what happens.
                    # Let's say if we have pos_qty == 2.0:
                    # TP fills 1.0, and SL fills the remaining 1.0 on the same bar.
                    # So exits[i] is True (partial or full).
                    exits[i] = True
                    pos_qty = 0.0
                    entry_px = 0.0
                elif hit_tp:
                    if pos_qty == 2.0:
                        # Exit half
                        exits[i] = True
                        pos_qty = 1.0
                        # entry_px remains the same
                    # If pos_qty was already 1.0, does HALF_TP trigger again?
                    # "qty_percent=50" on HALF_TP. In Pine, once HALF_TP is filled for an entry, it won't fill again.
                    # So if pos_qty == 1.0, HALF_TP cannot fill again. Only REST_SL can fill.
                elif hit_sl:
                    exits[i] = True
                    pos_qty = 0.0
                    entry_px = 0.0

            # 2. Check for entries on bar i (which executes at open of bar i+1)
            # "enterLong = hour == 1 and minute == 15 and strategy.position_size == 0"
            # This is evaluated on bar i. If true, we enter on bar i+1 open.
            # Since entries are only allowed when position_size == 0, we check pos_qty == 0.
            if hours[i] == 1 and minutes[i] == 15 and pos_qty == 0.0:
                entries[i+1] = True
                pos_qty = 2.0
                entry_px = open_p[i+1] # Filled at next bar's open

        return entries, short_entries, exits, short_exits

    entries, short_entries, exits, short_exits = logic_loop(open_p, high_p, low_p, close_p, hours, minutes)

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
