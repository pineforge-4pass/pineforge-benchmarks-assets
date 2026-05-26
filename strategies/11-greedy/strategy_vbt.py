import pandas as pd
import numpy as np
import vectorbt as vbt

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    open_p = df['open'].values
    high_p = df['high'].values
    low_p = df['low'].values
    close_p = df['close'].values
    timestamps = df['timestamp'].values
    n = len(open_p)

    days = timestamps // (24 * 3600 * 1000)

    entries = np.zeros(n, dtype=np.bool_)
    short_entries = np.zeros(n, dtype=np.bool_)
    exits = np.zeros(n, dtype=np.bool_)
    short_exits = np.zeros(n, dtype=np.bool_)
    execution_prices = open_p.copy()

    pos = 0
    entry_price = 0.0
    filled_today = 0
    last_day = -1

    long_gap_stop = np.nan
    short_gap_stop = np.nan
    long_up_stop = np.nan
    short_dn_stop = np.nan

    tp_price = np.nan
    sl_price = np.nan

    for i in range(1, n):
        day = days[i]
        if day != last_day:
            filled_today = 0
            last_day = day

        exited = False
        exit_p = 0.0

        if pos != 0 and filled_today < 5 and not np.isnan(tp_price):
            if pos == 1:
                if open_p[i] >= tp_price:
                    exit_p = open_p[i]
                    exited = True
                elif open_p[i] <= sl_price:
                    exit_p = open_p[i]
                    exited = True
                elif low_p[i] <= sl_price and high_p[i] >= tp_price:
                    if open_p[i] >= close_p[i]:
                        exit_p = sl_price
                    else:
                        exit_p = tp_price
                    exited = True
                elif high_p[i] >= tp_price:
                    exit_p = tp_price
                    exited = True
                elif low_p[i] <= sl_price:
                    exit_p = sl_price
                    exited = True
            elif pos == -1:
                if open_p[i] <= tp_price:
                    exit_p = open_p[i]
                    exited = True
                elif open_p[i] >= sl_price:
                    exit_p = open_p[i]
                    exited = True
                elif low_p[i] <= tp_price and high_p[i] >= sl_price:
                    if open_p[i] >= close_p[i]:
                        exit_p = tp_price
                    else:
                        exit_p = sl_price
                    exited = True
                elif low_p[i] <= tp_price:
                    exit_p = tp_price
                    exited = True
                elif high_p[i] >= sl_price:
                    exit_p = sl_price
                    exited = True

            if exited:
                if pos == 1:
                    exits[i] = True
                else:
                    short_exits[i] = True
                execution_prices[i] = exit_p
                pos = 0
                filled_today += 1

        if pos == 0 and filled_today < 5:
            entered = False
            ent_p = 0.0
            ent_dir = 0

            if not np.isnan(long_gap_stop):
                if open_p[i] >= long_gap_stop:
                    ent_p = open_p[i]
                    entered = True
                    ent_dir = 1
                elif high_p[i] >= long_gap_stop:
                    ent_p = long_gap_stop
                    entered = True
                    ent_dir = 1
            elif not np.isnan(long_up_stop):
                if open_p[i] >= long_up_stop:
                    ent_p = open_p[i]
                    entered = True
                    ent_dir = 1
                elif high_p[i] >= long_up_stop:
                    ent_p = long_up_stop
                    entered = True
                    ent_dir = 1

            if not entered:
                if not np.isnan(short_gap_stop):
                    if open_p[i] <= short_gap_stop:
                        ent_p = open_p[i]
                        entered = True
                        ent_dir = -1
                    elif low_p[i] <= short_gap_stop:
                        ent_p = short_gap_stop
                        entered = True
                        ent_dir = -1
                elif not np.isnan(short_dn_stop):
                    if open_p[i] <= short_dn_stop:
                        ent_p = open_p[i]
                        entered = True
                        ent_dir = -1
                    elif low_p[i] <= short_dn_stop:
                        ent_p = short_dn_stop
                        entered = True
                        ent_dir = -1

            if entered:
                pos = ent_dir
                entry_price = ent_p
                if pos == 1:
                    entries[i] = True
                else:
                    short_entries[i] = True
                execution_prices[i] = entry_price
                filled_today += 1

        upGap = open_p[i] > high_p[i-1] if i >= 1 else False
        dnGap = open_p[i] < low_p[i-1] if i >= 1 else False
        dn = pos < 0 and open_p[i] > close_p[i]
        up = pos > 0 and open_p[i] < close_p[i]

        if upGap and pos <= 0:
            long_gap_stop = high_p[i-1] if i >= 1 else np.nan
        else:
            long_gap_stop = np.nan

        if dnGap and pos >= 0:
            short_gap_stop = low_p[i-1] if i >= 1 else np.nan
        else:
            short_gap_stop = np.nan

        if dn and pos >= 0:
            short_dn_stop = close_p[i]
        else:
            short_dn_stop = np.nan

        if up and pos <= 0:
            long_up_stop = close_p[i]
        else:
            long_up_stop = np.nan

        revCond = dnGap if pos > 0 else upGap if pos < 0 else False
        if not revCond and pos != 0:
            if pos == 1:
                tp_price = entry_price + 10 * 0.01
                sl_price = entry_price - 10 * 0.01
            else:
                tp_price = entry_price - 10 * 0.01
                sl_price = entry_price + 10 * 0.01
        else:
            tp_price = np.nan
            sl_price = np.nan

    return vbt.Portfolio.from_signals(
        df['close'],
        entries=pd.Series(entries, index=df.index),
        short_entries=pd.Series(short_entries, index=df.index),
        exits=pd.Series(exits, index=df.index),
        short_exits=pd.Series(short_exits, index=df.index),
        price=pd.Series(execution_prices, index=df.index),
        init_cash=1000000,
        fees=fees,
        slippage=0.0,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
