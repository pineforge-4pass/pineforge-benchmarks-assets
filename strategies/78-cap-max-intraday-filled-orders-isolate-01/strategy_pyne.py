"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, currency, input, script, strategy, ta


@script.strategy("PF probe 97b - intraday cap isolate", shorttitle="PF_p97b_CAP", overlay=True, initial_capital=1000000, currency=currency.USD, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    i_fast=input.int(5, "Fast MA", minval=2),
    i_slow=input.int(13, "Slow MA", minval=3),
    i_max_fills=input.int(5, "Max intraday filled orders", minval=1)
):
    strategy.risk.max_intraday_filled_orders(i_max_fills)

    fast: float = ta.sma(close, i_fast)
    slow: float = ta.sma(close, i_slow)
    go_long: bool = ta.crossover(fast, slow)
    go_short: bool = ta.crossunder(fast, slow)

    if go_long and strategy.position_size <= 0:
        strategy.entry('L', strategy.long, comment='ma cross up')

    if go_short and strategy.position_size >= 0:
        strategy.entry('S', strategy.short, comment='ma cross dn')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
