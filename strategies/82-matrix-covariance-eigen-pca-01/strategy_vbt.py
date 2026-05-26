import pandas as pd
import numpy as np
import vectorbt as vbt

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    length = 14
    close = df['close']
    open_val = df['open']
    high = df['high']
    low = df['low']

    v1 = close - open_val
    v2 = high - low

    v1_mean = v1.rolling(length).mean()
    v2_mean = v2.rolling(length).mean()

    cov11 = ((v1 - v1_mean) ** 2).rolling(length).mean()
    cov12 = ((v1 - v1_mean) * (v2 - v2_mean)).rolling(length).mean()
    cov22 = ((v2 - v2_mean) ** 2).rolling(length).mean()

    # Analytical eigenvalue formula for 2x2 symmetric matrix:
    # trace = cov11 + cov22
    # det = cov11 * cov22 - cov12 * cov12
    # lambda = (trace + sqrt(trace^2 - 4 * det)) / 2
    #        = (cov11 + cov22 + sqrt((cov11 - cov22)^2 + 4 * cov12^2)) / 2
    term = np.sqrt((cov11 - cov22) ** 2 + 4 * (cov12 ** 2))
    lam = 0.5 * (cov11 + cov22 + term)

    lamSma = lam.rolling(length).mean()

    covReady = lam.notna() & lamSma.notna()

    entries = covReady & (lam > lamSma) & (lam.shift(1) <= lamSma.shift(1))
    short_entries = covReady & (lam < lamSma) & (lam.shift(1) >= lamSma.shift(1))

    return vbt.Portfolio.from_signals(
        close,
        entries=entries.shift(1).fillna(False),
        short_entries=short_entries.shift(1).fillna(False),
        price=open_val,
        fees=fees,
        init_cash=1000000,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
