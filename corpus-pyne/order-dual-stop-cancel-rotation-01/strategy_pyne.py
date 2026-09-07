"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import high, hour, low, script, strategy, syminfo


@script.strategy("PF probe 63 - dual stop cancel rotation", shorttitle="PF_P63_DUALCANCEL", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    useLongStop = hour < 12
    if useLongStop:
        strategy.entry('LE', strategy.long, stop=high + syminfo.mintick, comment='rotating long stop')
        strategy.cancel('SE')
    else:
        strategy.entry('SE', strategy.short, stop=low - syminfo.mintick, comment='rotating short stop')
        strategy.cancel('LE')

    if strategy.position_size > 0 and (not useLongStop):
        strategy.close('LE', comment='long regime close')

    if strategy.position_size < 0 and useLongStop:
        strategy.close('SE', comment='short regime close')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
