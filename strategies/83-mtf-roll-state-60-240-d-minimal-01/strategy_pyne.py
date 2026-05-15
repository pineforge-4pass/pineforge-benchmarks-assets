"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import barmerge, close, currency, high, request, script, strategy, syminfo, ta
from pynecore.types import Series


@script.strategy("PF probe 54 - MTF roll state", shorttitle="PF_P54_MTF", overlay=True, initial_capital=1000000, currency=currency.USD, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    h60: Series = request.security(syminfo.tickerid, '60', close, lookahead=barmerge.lookahead_off)
    h240: Series = request.security(syminfo.tickerid, '240', close, lookahead=barmerge.lookahead_off)
    dHigh1: Series = request.security(syminfo.tickerid, 'D', high[1], lookahead=barmerge.lookahead_off)

    roll60 = ta.change(h60) != 0
    roll240 = ta.change(h240) != 0
    dailyBreak = close > dHigh1 and close[1] <= dHigh1[1]

    if roll60 and h60 > h60[1] and (h240 >= h240[1]) and (strategy.position_size == 0):
        strategy.entry('R60', strategy.long, qty=1, comment='60 up with 240 state')

    if roll240 and h240 < h240[1] and (strategy.position_size > 0):
        strategy.close('R60', comment='240 down close')

    if dailyBreak and strategy.position_size == 0:
        strategy.entry('D', strategy.long, qty=1, comment='daily high break')

    if strategy.position_size > 0 and close < dHigh1 * 0.995:
        strategy.close_all(comment='daily ref close')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
