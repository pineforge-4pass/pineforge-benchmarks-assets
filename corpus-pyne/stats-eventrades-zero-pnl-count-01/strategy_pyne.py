"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, display, hour, minute, na, plot, script, strategy
from pynecore.types import Persistent


@script.strategy("PF-F: eventrades count", shorttitle="PF_F_EVTRADES", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    entry_price: Persistent[float] = na(float)
    if hour == 0 and minute == 0 and (strategy.position_size == 0):
        strategy.entry('LE', strategy.long, qty=1, comment='even-trade entry')
        entry_price = close

    if strategy.position_size > 0 and (not na(entry_price)):
        strategy.exit('LX', 'LE', limit=entry_price, comment='even-trade exit @ entry')

    plot(strategy.eventrades, title='eventrades', display=display.none)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
