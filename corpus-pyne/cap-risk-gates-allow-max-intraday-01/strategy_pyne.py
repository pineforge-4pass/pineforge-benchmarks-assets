"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import hour, minute, script, strategy


@script.strategy("PF TV golden 46 - risk gates", shorttitle="PF_G46_RISK", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=10, process_orders_on_close=False)
def main():
    strategy.risk.allow_entry_in(strategy.direction.long)
    strategy.risk.max_position_size(2)
    strategy.risk.max_intraday_filled_orders(3)

    if hour == 0 and minute == 15:
        strategy.entry('L1', strategy.long, qty=1, comment='first long')

    if hour == 0 and minute == 30:
        strategy.entry('L2', strategy.long, qty=1, comment='second long')

    if hour == 0 and minute == 45:
        strategy.entry('L3', strategy.long, qty=1, comment='third long')

    if hour == 1 and minute == 0:
        strategy.entry('S_BLOCKED', strategy.short, qty=1, comment='blocked short')

    if hour == 3 and minute == 0 and (strategy.position_size != 0):
        strategy.close_all(comment='daily reset')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
