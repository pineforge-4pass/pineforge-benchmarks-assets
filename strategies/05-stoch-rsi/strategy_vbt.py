import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit
from speed.vbt_helpers import rsi, stoch

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close = df['close']
    open_val = df['open']

    rsi_val = rsi(close, 14)
    stoch_val = stoch(rsi_val, rsi_val, rsi_val, 14)
    stochK = stoch_val.rolling(3).mean()
    stochD = stochK.rolling(3).mean()

    long_cond = (stochK > stochD) & (stochK.shift(1) <= stochD.shift(1)) & (stochK < 20)
    short_cond = (stochK < stochD) & (stochK.shift(1) >= stochD.shift(1)) & (stochK > 80)

    long_exit_cond = (stochK > 80) & (stochK < stochD) & (stochK.shift(1) >= stochD.shift(1))
    short_exit_cond = (stochK < 20) & (stochK > stochD) & (stochK.shift(1) <= stochD.shift(1))

    long_cond_arr = long_cond.fillna(False).values
    short_cond_arr = short_cond.fillna(False).values
    long_exit_arr = long_exit_cond.fillna(False).values
    short_exit_arr = short_exit_cond.fillna(False).values

    @njit
    def simulate_signals_nb(lc, sc, le, se):
        n = len(lc)
        entries = np.zeros(n, dtype=np.bool_)
        short_entries = np.zeros(n, dtype=np.bool_)
        exits = np.zeros(n, dtype=np.bool_)
        short_exits = np.zeros(n, dtype=np.bool_)

        pos = 0
        for i in range(1, n):
            lc_prev = lc[i-1]
            sc_prev = sc[i-1]
            le_prev = le[i-1]
            se_prev = se[i-1]

            if pos == 1:
                if sc_prev:
                    short_entries[i] = True
                    pos = -1
                elif le_prev:
                    exits[i] = True
                    pos = 0
            elif pos == -1:
                if lc_prev:
                    entries[i] = True
                    pos = 1
                elif se_prev:
                    short_exits[i] = True
                    pos = 0
            else:
                if lc_prev:
                    entries[i] = True
                    pos = 1
                elif sc_prev:
                    short_entries[i] = True
                    pos = -1

        return entries, short_entries, exits, short_exits

    entries, short_entries, exits, short_exits = simulate_signals_nb(
        long_cond_arr, short_cond_arr, long_exit_arr, short_exit_arr
    )

    return vbt.Portfolio.from_signals(
        close,
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
