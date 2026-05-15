"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, currency, high, input, low, na, open, script, strategy, ta
from pynecore.types import Series


@script.strategy("PF probe 97c - range-expansion pending-stop isolate", shorttitle="PF_p97c_RNG", overlay=True, initial_capital=1000000, currency=currency.USD, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    i_atr_len=input.int(14, "ATR length", minval=1),
    i_atr_mult=input.float(1.0, "Range/ATR threshold", minval=0.1)
):

    prev_range: float = high[1] - low[1]
    atr_now: Series[float] = ta.atr(i_atr_len)
    atr_prev: float = atr_now[1]
    expansion: bool = not na(atr_prev) and prev_range > atr_prev * i_atr_mult

    prev_up: bool = close[1] > open[1]
    prev_down: bool = close[1] < open[1]

    arm_long: bool = expansion and prev_up
    arm_short: bool = expansion and prev_down

    if arm_long:
        strategy.entry('LongOnRng', strategy.long, stop=high[1])
    else:
        strategy.cancel('LongOnRng')

    if arm_short:
        strategy.entry('ShortOnRng', strategy.short, stop=low[1])
    else:
        strategy.cancel('ShortOnRng')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
