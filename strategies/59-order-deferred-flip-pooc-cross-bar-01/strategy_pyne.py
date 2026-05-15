"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import currency, dayofweek, high, hour, low, minute, script, strategy


@script.strategy("PF probe 96 - multi-cycle POOC cross-bar", shorttitle="PF_P96_POOC", overlay=True, initial_capital=1000000, currency=currency.USD, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=True)
def main():
    isDown = hour == 8 and minute == 0
    isUp = hour == 14 and minute == 0

    shortStop = high * 10.0
    longStop = low * 0.1

    if isDown:
        strategy.entry('SE', strategy.short, qty=1, stop=shortStop, comment='open-guaranteed short')
        strategy.cancel('LE')

    if isUp:
        strategy.entry('LE', strategy.long, qty=1, stop=longStop, comment='open-guaranteed long')
        strategy.cancel('SE')

    if isDown and strategy.position_size > 0:
        strategy.close('LE', comment='flip flat long')

    if isUp and strategy.position_size < 0:
        strategy.close('SE', comment='flip flat short')

    if dayofweek == 2 and hour == 0 and (minute == 0) and (strategy.position_size != 0):
        strategy.close_all(comment='weekly reset')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
