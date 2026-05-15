"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import currency, hour, minute, script, strategy, ta


@script.strategy("PF probe 50 - stop limit trail", shorttitle="PF_P50_EXIT3", overlay=True, initial_capital=1000000, currency=currency.USD, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    atr = ta.atr(14)
    enterLong = hour == 8 and minute == 15 and (strategy.position_size == 0)
    enterShort = hour == 16 and minute == 15 and (strategy.position_size == 0)

    if enterLong:
        strategy.entry('L', strategy.long, qty=1, comment='probe long')

    if enterShort:
        strategy.entry('S', strategy.short, qty=1, comment='probe short')

    if strategy.position_size > 0:
        longStop = strategy.position_avg_price - atr * 0.8
        longLimit = strategy.position_avg_price + atr * 1.6
        strategy.exit('LX', 'L', stop=longStop, limit=longLimit, trail_points=atr, comment='triple exit long')

    if strategy.position_size < 0:
        shortStop = strategy.position_avg_price + atr * 0.8
        shortLimit = strategy.position_avg_price - atr * 1.6
        strategy.exit('SX', 'S', stop=shortStop, limit=shortLimit, trail_points=atr, comment='triple exit short')

    if strategy.position_size != 0 and hour == 23 and (minute == 45):
        strategy.close_all(comment='timeout')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
