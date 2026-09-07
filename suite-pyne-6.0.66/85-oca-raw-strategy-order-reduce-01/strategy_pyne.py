"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import currency, hour, math, minute, script, strategy


@script.strategy("PF TV golden 44 - OCA reduce", shorttitle="PF_G44_OCA", overlay=True, initial_capital=1000000, currency=currency.USD, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    if hour == 7 and minute == 15 and (strategy.position_size == 0):
        strategy.entry('L', strategy.long, qty=1, comment='oca source')
    if strategy.position_size > 0:
        qty = math.abs(strategy.position_size)
        entry = strategy.position_avg_price
        strategy.order('TP', strategy.short, qty=qty, limit=entry * 1.004, oca_name='BRACKET', oca_type=strategy.oca.reduce)

        strategy.order('SL', strategy.short, qty=qty, stop=entry * 0.996, oca_name='BRACKET', oca_type=strategy.oca.reduce)

    if strategy.position_size == 0:
        strategy.cancel('TP')
        strategy.cancel('SL')

    if strategy.position_size > 0 and hour == 13 and (minute == 15):
        strategy.close('L', comment='timeout')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
