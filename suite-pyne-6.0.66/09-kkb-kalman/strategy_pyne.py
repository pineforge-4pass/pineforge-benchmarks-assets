"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barstate, close, color, currency, input, math, na, plot, script,
    strategy, ta
)
from pynecore.types import Persistent


@script.strategy("Kinetic Kalman Breakout", shorttitle="KKB", overlay=True, margin_long=100, margin_short=100, use_bar_magnifier=False, initial_capital=1000000, currency=currency.USD, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    processNoisePos=input.float(0.05, minval=0.001, title='Base Process Noise (Position)'),
    processNoiseVel=input.float(0.0001, minval=1e-05, title='Base Process Noise (Velocity)'),
    measurementNoise=input.float(250, minval=1, title='Base Measurement Noise (R)'),
    bandLookback=input.int(200, title='Band Lookback for Abs Error'),
    bandMultiplier=input.float(2.6, title='Band Multiplier', step=0.1),
    m=input.float(7.88, minval=0.1, step=0.1, title='ATR Trailing Multiplier (Ref)')
):

    x_p: Persistent[float] = na(float)
    x_v: Persistent[float] = na(float)
    p00: Persistent[float] = na(float)
    p01: Persistent[float] = na(float)
    p10: Persistent[float] = na(float)
    p11: Persistent[float] = na(float)

    if barstate.isfirst:
        x_p = close
        x_v = 0.0
        p00 = 1.0
        p01 = 0.0
        p10 = 0.0
        p11 = 1.0

    pPrime = x_p + x_v
    vPrime = x_v

    a00 = 1 * p00 + 1 * p10
    a01 = 1 * p01 + 1 * p11
    a10 = 0 * p00 + 1 * p10
    a11 = 0 * p01 + 1 * p11

    p00_ = a00 * 1 + a01 * 1
    p01_ = a00 * 0 + a01 * 1
    p10_ = a10 * 1 + a11 * 1
    p11_ = a10 * 0 + a11 * 1

    p00_ += processNoisePos
    p11_ += processNoiseVel

    z = close
    y = z - pPrime
    S = p00_ + measurementNoise
    K0 = p00_ / S
    K1 = p10_ / S

    x_p_upd = pPrime + K0 * y
    x_v_upd = vPrime + K1 * y

    i00 = 1 - K0
    i01: float = 0.0
    i10 = -K1
    i11: float = 1.0

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

    kalmanPrice = x_p

    absDiff = math.abs(close - kalmanPrice)
    mae = ta.sma(absDiff, bandLookback)
    upperBand = kalmanPrice + bandMultiplier * mae
    lowerBand = kalmanPrice - bandMultiplier * mae

    bullSignal = ta.crossover(close, upperBand)
    bearSignal = ta.crossunder(close, lowerBand)

    if bullSignal:
        strategy.entry('Long', strategy.long)

    if bearSignal:
        strategy.entry('Short', strategy.short)

    plot(kalmanPrice, color=color.new(color.blue, 0), title='Kalman Filter')
    plot(upperBand, color=color.new(color.gray, 60), title='Upper Band')
    plot(lowerBand, color=color.new(color.gray, 60), title='Lower Band')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
