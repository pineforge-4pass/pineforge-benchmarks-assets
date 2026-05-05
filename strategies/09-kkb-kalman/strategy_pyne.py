"""@pyne
Hand-port of strategies/09-kkb-kalman/strategy.pine for PyneCore.

Pine source: "Kinetic Kalman Breakout (KKB)" — runs a hand-rolled
2-state Kalman filter over the close-price series, then issues
breakouts when close crosses an MAE-scaled band around the filter
output.

Persistent state (Kalman position/velocity, 2x2 covariance matrix) is
maintained via PyneCore's `Persistent[float]` annotation, which mirrors
Pine's `var float`.
"""
from pynecore import Persistent
from pynecore.lib import script, input, ta, math, strategy, barstate, close


@script.strategy("Kinetic Kalman Breakout", shorttitle="KKB", overlay=True,
                 margin_long=100, margin_short=100)
def main(
    process_noise_pos: float = input.float(0.05, minval=0.001,
                                            title="Base Process Noise (Position)"),
    process_noise_vel: float = input.float(0.0001, minval=0.00001,
                                            title="Base Process Noise (Velocity)"),
    measurement_noise: float = input.float(250, minval=1,
                                            title="Base Measurement Noise (R)"),
    band_lookback: int = input.int(200, title="Band Lookback for Abs Error"),
    band_multiplier: float = input.float(2.6, title="Band Multiplier", step=0.1),
    _atr_mult_ref: float = input.float(7.88, minval=0.1, step=0.1,
                                        title="ATR Trailing Multiplier (Ref)"),
):
    x_p: Persistent[float] = float("nan")
    x_v: Persistent[float] = float("nan")
    p00: Persistent[float] = float("nan")
    p01: Persistent[float] = float("nan")
    p10: Persistent[float] = float("nan")
    p11: Persistent[float] = float("nan")

    if barstate.isfirst:
        x_p = close
        x_v = 0.0
        p00 = 1.0
        p01 = 0.0
        p10 = 0.0
        p11 = 1.0

    # PREDICT
    p_prime = x_p + x_v
    v_prime = x_v

    a00 = p00 + p10
    a01 = p01 + p11
    a10 = p10
    a11 = p11

    p00_ = a00 + a01
    p01_ = a01
    p10_ = a10 + a11
    p11_ = a11

    p00_ += process_noise_pos
    p11_ += process_noise_vel

    # UPDATE
    z = close
    y = z - p_prime
    s = p00_ + measurement_noise
    k0 = p00_ / s
    k1 = p10_ / s

    x_p_upd = p_prime + k0 * y
    x_v_upd = v_prime + k1 * y

    i00 = 1 - k0
    i01 = 0.0
    i10 = -k1
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

    kalman_price = x_p

    # BANDS
    abs_diff = math.abs(close - kalman_price)
    mae = ta.sma(abs_diff, band_lookback)
    upper_band = kalman_price + band_multiplier * mae
    lower_band = kalman_price - band_multiplier * mae

    # SIGNALS (reversals)
    bull_signal = ta.crossover(close, upper_band)
    bear_signal = ta.crossunder(close, lower_band)

    if bull_signal:
        strategy.entry("Long", strategy.long)
    if bear_signal:
        strategy.entry("Short", strategy.short)
