"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import bar_index, close, currency, dayofweek, hour, math, minute, script, strategy


@script.strategy("Parity probe 05 - small equity fraction", shorttitle="par_p05", overlay=True, initial_capital=1000000, currency=currency.USD, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=0, process_orders_on_close=False)
def main():
    fire: bool = dayofweek == 2 and hour == 0 and (minute == 0) and (strategy.position_size == 0)
    qty_dyn: float = math.round(strategy.equity / close * 100) / 1000

    if fire and qty_dyn > 0:
        strategy.entry('E', strategy.long, qty=qty_dyn, comment='qty = 10% equity / close')

    if strategy.position_size > 0 and bar_index > strategy.opentrades.entry_bar_index(0):
        strategy.close('E', comment='next-bar flatten')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
