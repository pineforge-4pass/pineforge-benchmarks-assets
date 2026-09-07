"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import hour, minute, script, strategy


@script.strategy("PF-F: max_contracts_held gate", shorttitle="PF_F_MCH", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=10, process_orders_on_close=False)
def main():
    gate_open: bool = strategy.max_contracts_held_all < 5
    if minute == 0 and gate_open:
        strategy.entry('LE', strategy.long, qty=1, comment='pyramid-add')

    if hour == 23 and minute == 45 and (strategy.position_size != 0):
        strategy.close_all(comment='daily-exit')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
