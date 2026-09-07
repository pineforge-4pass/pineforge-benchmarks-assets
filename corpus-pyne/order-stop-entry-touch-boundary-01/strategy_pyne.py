"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import high, hour, low, minute, script, strategy, syminfo


@script.strategy("PF probe 53 - stop touch boundary", shorttitle="PF_P53_TOUCH", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    tick = syminfo.mintick
    longStop = high[1] + tick
    shortStop = low[1] - tick

    longWindow = hour == 2 and minute == 15
    shortWindow = hour == 14 and minute == 15

    if longWindow and strategy.position_size == 0:
        strategy.entry('LE', strategy.long, stop=longStop, comment='one tick over high')
        strategy.cancel('SE')

    if shortWindow and strategy.position_size == 0:
        strategy.entry('SE', strategy.short, stop=shortStop, comment='one tick under low')
        strategy.cancel('LE')

    if strategy.position_size > 0 and hour == 6 and (minute == 15):
        strategy.close('LE', comment='long timeout')

    if strategy.position_size < 0 and hour == 18 and (minute == 15):
        strategy.close('SE', comment='short timeout')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
