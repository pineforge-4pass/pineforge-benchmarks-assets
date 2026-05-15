"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import barstate, close, currency, script, strategy, ta
from pynecore.types import Persistent


@script.strategy("PF barstate-magnifier probe 01a - isconfirmed ON", shorttitle="BSM_01a_ON", overlay=True, initial_capital=1000000, currency=currency.USD, use_bar_magnifier=True, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    emaFast = ta.ema(close, 9)
    emaSlow = ta.ema(close, 21)

    pendingLong: Persistent[bool] = False
    pendingExit: Persistent[bool] = False

    if ta.crossover(emaFast, emaSlow):
        pendingLong = True
    if ta.crossunder(emaFast, emaSlow):
        pendingExit = True

    if barstate.isconfirmed and pendingLong and (strategy.position_size == 0):
        strategy.entry('L', strategy.long, qty=1, comment='confirmed long')
        pendingLong = False

    if barstate.isconfirmed and pendingExit and (strategy.position_size > 0):
        strategy.close('L', comment='confirmed exit')
        pendingExit = False


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
