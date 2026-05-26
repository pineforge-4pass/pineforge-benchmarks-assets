import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close = df['close'].values
    high = df['high'].values
    low = df['low'].values
    open_val = df['open'].values
    n = len(df)

    processNoisePos = 0.05
    processNoiseVel = 0.0001
    measurementNoise = 250.0
    bandLookback = 200
    bandMultiplier = 2.6

    @njit
    def run_kalman_and_signals(close, high, low):
        # Arrays to hold Kalman states
        kalmanPrice = np.empty(n, dtype=np.float64)

        x_p = close[0]
        x_v = 0.0
        p00 = 1.0
        p01 = 0.0
        p10 = 0.0
        p11 = 1.0

        kalmanPrice[0] = x_p

        # Run Kalman Filter loop
        for i in range(1, n):
            # PREDICT
            pPrime = x_p + x_v
            vPrime = x_v

            a00 = p00 + p10
            a01 = p01 + p11
            a10 = p10
            a11 = p11

            p00_ = a00 + a01
            p01_ = a01
            p10_ = a10 + a11
            p11_ = a11

            p00_ += processNoisePos
            p11_ += processNoiseVel

            # UPDATE
            z = close[i]
            y = z - pPrime
            S = p00_ + measurementNoise
            K0 = p00_ / S
            K1 = p10_ / S

            x_p_upd = pPrime + K0 * y
            x_v_upd = vPrime + K1 * y

            i00 = 1.0 - K0
            i01 = 0.0
            i10 = -K1
            i11 = 1.0

            pp00 = i00 * p00_ + i01 * p10_
            pp01 = i00 * p01_ + i01 * p11_
            pp10 = i10 * p00_ + i11 * p10_
            pp11 = i10 * p01_ + i11 * p11_

            x_p = x_p_upd
            x_v = x_v_upd
            p00 = pp00
            p01 = pp01
            p10 = pp10
            p11 = pp11

            kalmanPrice[i] = x_p

        return kalmanPrice

    kalmanPrice_arr = run_kalman_and_signals(close, high, low)
    kalmanPrice = pd.Series(kalmanPrice_arr, index=df.index)

    # MAE calculation (ta.sma of absolute difference)
    absDiff = (df['close'] - kalmanPrice).abs()
    mae = absDiff.rolling(bandLookback).mean().fillna(0.0)

    upperBand = kalmanPrice + bandMultiplier * mae
    lowerBand = kalmanPrice - bandMultiplier * mae

    # Signal logic
    bullSignal = (df['close'] > upperBand) & (df['close'].shift(1) <= upperBand.shift(1))
    bearSignal = (df['close'] < lowerBand) & (df['close'].shift(1) >= lowerBand.shift(1))

    # Shift signal by 1 for execution on next bar open (process_orders_on_close = false)
    entries = bullSignal.shift(1).fillna(False)
    short_entries = bearSignal.shift(1).fillna(False)

    return vbt.Portfolio.from_signals(
        df['close'],
        entries=entries,
        short_entries=short_entries,
        price=df['open'],
        init_cash=1000000,
        fees=fees,
        slippage=0.0,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
