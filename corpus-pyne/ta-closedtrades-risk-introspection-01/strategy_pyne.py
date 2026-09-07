"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, high, low, script, strategy, ta
from pynecore.types import Series


@script.strategy("Advanced Trade Metrics", overlay=True, initial_capital=1000000, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main():
    strategy.risk.max_drawdown(20, strategy.percent_of_equity)
    hh: Series = ta.highest(high, 20)
    ll: Series = ta.lowest(low, 20)

    qty: float = 1.0
    if strategy.closedtrades > 0:
        last_profit = strategy.closedtrades.profit(strategy.closedtrades - 1)
        if last_profit < 0:
            qty = 0.5
        else:
            qty = 2.0

    if close > hh[1]:
        strategy.entry('Long', strategy.long, qty=qty)
    if close < ll[1]:
        strategy.entry('Short', strategy.short, qty=qty)

    if strategy.opentrades > 0:
        open_dd = strategy.opentrades.max_drawdown(0)
        if open_dd > 1000:
            strategy.close('Long')
            strategy.close('Short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
