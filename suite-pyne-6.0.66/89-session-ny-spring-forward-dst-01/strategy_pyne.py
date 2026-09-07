"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import currency, na, script, strategy, time, timeframe
from pynecore.types import Series


@script.strategy("PF session-dst probe 01 - NY spring forward", shorttitle="SDST_p01_NY", overlay=True, initial_capital=1000000, currency=currency.USD, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    sessId: Series[int] = time(timeframe.period, '0930-1600', 'America/New_York')
    inSess: bool = not na(sessId)
    wasInSess: bool = not na(sessId[1])

    sessOpen: bool = inSess and (not wasInSess)
    sessClose: bool = wasInSess and (not inSess)

    if sessOpen and strategy.position_size == 0:
        strategy.entry('L', strategy.long, qty=1, comment='session open')
    if sessClose and strategy.position_size > 0:
        strategy.close('L', comment='session close')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
