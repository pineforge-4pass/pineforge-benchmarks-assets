"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import currency, hour, minute, script, strategy


@script.strategy("PF TV golden 42 - close immediate", shorttitle="PF_G42_CLOSE", overlay=True, initial_capital=1000000, currency=currency.USD, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    if hour == 2 and minute == 15 and (strategy.position_size == 0):
        strategy.entry('NEXT', strategy.long, qty=1, comment='normal close case')
    if hour == 3 and minute == 15 and (strategy.position_size > 0):
        strategy.close('NEXT', comment='normal close')

    if hour == 10 and minute == 15 and (strategy.position_size == 0):
        strategy.entry('IMM', strategy.long, qty=1, comment='immediate close case')

    if hour == 11 and minute == 15 and (strategy.position_size > 0):
        strategy.close('IMM', comment='immediate close', immediately=True)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)