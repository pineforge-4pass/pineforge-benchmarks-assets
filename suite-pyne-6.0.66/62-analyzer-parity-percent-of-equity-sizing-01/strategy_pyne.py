"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import bar_index, currency, dayofweek, hour, minute, script, strategy


@script.strategy("Parity probe 04 - percent_of_equity sizing", shorttitle="par_p04", overlay=True, initial_capital=1000000, currency=currency.USD, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.percent_of_equity, default_qty_value=99, pyramiding=0, process_orders_on_close=False)
def main():
    fire: bool = dayofweek == 2 and hour == 0 and (minute == 0) and (strategy.position_size == 0)
    if fire:
        strategy.entry('E', strategy.long, comment='auto-sized 99% equity')

    if strategy.position_size > 0 and bar_index > strategy.opentrades.entry_bar_index(0):
        strategy.close('E', comment='next-bar flatten')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
