"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, high, input, low, script, strategy, ta
from pynecore.types import Series


@script.strategy("PF IES probe 04 - pressure gauge", shorttitle="IES_p04_PRESS", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_pressure_len=input.int(14, "Pressure Period", minval=5, maxval=50),
    i_pressure_smooth=input.int(5, "Pressure Smoothing", minval=1, maxval=20),
    i_pressure_mom=input.int(10, "Pressure Momentum", minval=3, maxval=30),
    i_pressure_high=input.float(0.7, "Extreme Buy Level", minval=0.5, maxval=0.9, step=0.05),
    i_pressure_low=input.float(0.3, "Extreme Sell Level", minval=0.1, maxval=0.5, step=0.05),
    i_pressure_thresh=input.float(0.05, "Momentum Threshold", minval=0.01, maxval=0.2, step=0.01)
):

    range_val: float = high - low
    raw_buy: float = (close - low) / range_val if range_val > 0 else 0.5

    pressure_ratio: float = ta.ema(raw_buy, i_pressure_len)
    pressure_smooth: Series[float] = ta.ema(pressure_ratio, i_pressure_smooth)
    pressure_momentum: float = pressure_smooth - pressure_smooth[i_pressure_mom]

    pressure_state: int = 0
    if pressure_smooth >= i_pressure_high:
        pressure_state = 2
    elif pressure_smooth > 0.5 + i_pressure_thresh:
        pressure_state = 1
    elif pressure_smooth <= i_pressure_low:
        pressure_state = -2
    elif pressure_smooth < 0.5 - i_pressure_thresh:
        pressure_state = -1

    pressure_bull: Series[bool] = pressure_state >= 1 or pressure_momentum > i_pressure_thresh
    pressure_bear: Series[bool] = pressure_state <= -1 or pressure_momentum < -i_pressure_thresh

    long_entry: bool = pressure_bull and (not pressure_bull[1]) and (strategy.position_size <= 0)
    short_entry: bool = pressure_bear and (not pressure_bear[1]) and (strategy.position_size >= 0)

    if long_entry:
        if strategy.position_size < 0:
            strategy.close('S', comment='flip')
        strategy.entry('L', strategy.long, qty=1, comment='pressure bull')

    if short_entry:
        if strategy.position_size > 0:
            strategy.close('L', comment='flip')
        strategy.entry('S', strategy.short, qty=1, comment='pressure bear')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
