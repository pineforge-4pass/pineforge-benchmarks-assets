"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, hour, minute, script, strategy


@script.strategy("PF probe 81 - dual stop near only", shorttitle="PF_P81_NEAR", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    if hour == 2 and minute == 45 and (strategy.position_size == 0):
        strategy.entry('LE', strategy.long, stop=close * 1.002, comment='near long stop')
        strategy.entry('SE', strategy.short, stop=close * 0.998, comment='near short stop')

    if strategy.position_size != 0 and hour == 6 and (minute == 15):
        strategy.close_all(comment='morning flat')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
