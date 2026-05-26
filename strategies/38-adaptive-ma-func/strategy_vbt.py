import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close_p = df['close'].values
    open_p = df['open'].values
    n = len(df)

    @njit
    def adaptive_ma_loop_nb(close_p, open_p):
        er = np.zeros(n)
        sc = np.zeros(n)
        kama = np.zeros(n)

        fastAlpha = 2.0 / 3.0
        slowAlpha = 2.0 / 31.0

        abs_diff = np.zeros(n)
        for i in range(1, n):
            abs_diff[i] = abs(close_p[i] - close_p[i-1])

        for i in range(n):
            if i < 14:
                er[i] = 0.0
            else:
                direction = abs(close_p[i] - close_p[i-14])
                volatilitySum = 0.0
                for j in range(14):
                    volatilitySum += abs_diff[i-j]
                if volatilitySum != 0.0:
                    er[i] = direction / volatilitySum
                else:
                    er[i] = 0.0

            sc[i] = (er[i] * (fastAlpha - slowAlpha) + slowAlpha) ** 2

            if i == 0:
                kama[i] = sc[i] * close_p[i]
            else:
                kama[i] = kama[i-1] + sc[i] * (close_p[i] - kama[i-1])

        entries = np.zeros(n, dtype=np.bool_)
        short_entries = np.zeros(n, dtype=np.bool_)

        pos = 0

        for i in range(2, n):
            kamaUp = kama[i-1] > kama[i-2]
            kamaDown = kama[i-1] < kama[i-2]
            kamaUp_prev = kama[i-2] > kama[i-3]
            kamaDown_prev = kama[i-2] < kama[i-3]

            longCond = kamaUp and not kamaUp_prev
            shortCond = kamaDown and not kamaDown_prev

            if pos == 1:
                if shortCond:
                    short_entries[i] = True
                    pos = -1
            elif pos == -1:
                if longCond:
                    entries[i] = True
                    pos = 1
            else:
                if longCond:
                    entries[i] = True
                    pos = 1
                elif shortCond:
                    short_entries[i] = True
                    pos = -1

        return entries, short_entries

    entries, short_entries = adaptive_ma_loop_nb(close_p, open_p)

    return vbt.Portfolio.from_signals(
        df['close'],
        entries=pd.Series(entries, index=df.index),
        short_entries=pd.Series(short_entries, index=df.index),
        price=df['open'],
        init_cash=1000000,
        fees=fees,
        slippage=0.0,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
