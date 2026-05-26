import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit
from speed.vbt_helpers import rsi

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close = df['close']
    open_val = df['open']

    ema7 = close.ewm(span=7, adjust=False).mean()
    ema21 = close.ewm(span=21, adjust=False).mean()
    ema50 = close.ewm(span=50, adjust=False).mean()
    ema200 = close.ewm(span=200, adjust=False).mean()

    rsi_val = rsi(close, 14)

    bullish_macro = ema50 > ema200
    bearish_macro = ema50 < ema200

    rsi_long_ok = (rsi_val > 50) & (rsi_val < 70)
    rsi_short_ok = (rsi_val < 50) & (rsi_val > 30)

    long_trigger = ((ema7 > ema21) & (ema7.shift(1) <= ema21.shift(1))) & rsi_long_ok
    short_trigger = ((ema7 < ema21) & (ema7.shift(1) >= ema21.shift(1))) & rsi_short_ok

    long_exit = ((ema7 < ema21) & (ema7.shift(1) >= ema21.shift(1))) | (close < ema50)
    short_exit = ((ema7 > ema21) & (ema7.shift(1) <= ema21.shift(1))) | (close > ema50)

    long_trigger_arr = (bullish_macro & long_trigger).fillna(False).values
    short_trigger_arr = (bearish_macro & short_trigger).fillna(False).values
    long_exit_arr = long_exit.fillna(False).values
    short_exit_arr = short_exit.fillna(False).values

    @njit
    def simulate_signals_nb(lt, st, le, se):
        n = len(lt)
        entries = np.zeros(n, dtype=np.bool_)
        short_entries = np.zeros(n, dtype=np.bool_)
        exits = np.zeros(n, dtype=np.bool_)
        short_exits = np.zeros(n, dtype=np.bool_)

        pos = 0
        for i in range(1, n):
            lt_prev = lt[i-1]
            st_prev = st[i-1]
            le_prev = le[i-1]
            se_prev = se[i-1]

            if pos == 1:
                if st_prev:
                    short_entries[i] = True
                    pos = -1
                elif le_prev:
                    exits[i] = True
                    pos = 0
            elif pos == -1:
                if lt_prev:
                    entries[i] = True
                    pos = 1
                elif se_prev:
                    short_exits[i] = True
                    pos = 0
            else:
                if lt_prev:
                    entries[i] = True
                    pos = 1
                elif st_prev:
                    short_entries[i] = True
                    pos = -1

        return entries, short_entries, exits, short_exits

    entries, short_entries, exits, short_exits = simulate_signals_nb(
        long_trigger_arr, short_trigger_arr, long_exit_arr, short_exit_arr
    )

    return vbt.Portfolio.from_signals(
        df['close'],
        entries=pd.Series(entries, index=df.index),
        short_entries=pd.Series(short_entries, index=df.index),
        exits=pd.Series(exits, index=df.index),
        short_exits=pd.Series(short_exits, index=df.index),
        price=open_val,
        init_cash=1000000,
        fees=fees,
        slippage=0.0,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
