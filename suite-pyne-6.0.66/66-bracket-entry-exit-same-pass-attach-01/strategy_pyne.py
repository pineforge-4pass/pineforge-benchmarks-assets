"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, currency, hour, minute, script, strategy


@script.strategy("PF probe 71 - entry exit same pass", shorttitle="PF_P71_ENTEXIT", overlay=True, initial_capital=1000000, currency=currency.USD, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    if hour == 8 and minute == 15 and (strategy.position_size == 0):
        strategy.entry('L', strategy.long, qty=1, comment='entry with bracket')
        strategy.exit('X', 'L', limit=close * 1.005, stop=close * 0.995, comment='same-pass bracket')

    if hour == 16 and minute == 15 and (strategy.position_size == 0):
        strategy.entry('S', strategy.short, qty=1, comment='short entry with bracket')
        strategy.exit('XS', 'S', limit=close * 0.995, stop=close * 1.005, comment='same-pass short bracket')

    if strategy.position_size != 0 and hour == 23 and (minute == 45):
        strategy.close_all(comment='timeout')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
