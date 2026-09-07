"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import hour, minute, script, strategy


@script.strategy("PF TV golden 45 - commission sizing", shorttitle="PF_G45_SIZE", overlay=True, initial_capital=1000000, commission_type=strategy.commission.cash_per_order, commission_value=1.5, slippage=0, default_qty_type=strategy.percent_of_equity, default_qty_value=25, pyramiding=1, process_orders_on_close=False)
def main():
    if hour == 8 and minute == 15 and (strategy.position_size == 0):
        strategy.entry('L', strategy.long, comment='default percent sizing')
    if hour == 12 and minute == 15 and (strategy.position_size > 0):
        strategy.close('L', comment='sizing close')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
