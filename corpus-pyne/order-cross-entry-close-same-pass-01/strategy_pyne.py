"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import hour, minute, script, strategy


@script.strategy("PF probe 68 - entry close same pass", shorttitle="PF_P68_ENTCLOSE", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    if hour == 0 and minute == 15 and (strategy.position_size == 0):
        strategy.entry('L', strategy.long, qty=1, comment='entry first')
        strategy.close('L', comment='close second')

    if hour == 6 and minute == 15 and (strategy.position_size == 0):
        strategy.close('L2', comment='close first')
        strategy.entry('L2', strategy.long, qty=1, comment='entry second')

    if hour == 7 and minute == 15 and (strategy.position_size > 0):
        strategy.close_all(comment='cleanup')

    if hour == 12 and minute == 15 and (strategy.position_size == 0):
        strategy.entry('S', strategy.short, qty=1, comment='short entry first')
        strategy.close('S', comment='short close second')

    if hour == 18 and minute == 15 and (strategy.position_size == 0):
        strategy.close('S2', comment='short close first')
        strategy.entry('S2', strategy.short, qty=1, comment='short entry second')

    if hour == 19 and minute == 15 and (strategy.position_size < 0):
        strategy.close_all(comment='short cleanup')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
