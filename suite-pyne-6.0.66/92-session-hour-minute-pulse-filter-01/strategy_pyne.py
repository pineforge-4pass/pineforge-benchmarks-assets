"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import currency, hour, minute, script, strategy


@script.strategy("PF TV golden 48 - time filter", shorttitle="PF_G48_TIME", overlay=True, initial_capital=1000000, currency=currency.USD, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    entryPulse = hour == 0 and minute == 15
    exitPulse = hour == 0 and minute == 45

    if entryPulse and strategy.position_size == 0:
        strategy.entry('T', strategy.long, qty=1, comment='time entry')

    if exitPulse and strategy.position_size > 0:
        strategy.close('T', comment='time exit')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
