"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, high, low, open, script, strategy


@script.strategy("PF probe 98 - inside-bar engulf", shorttitle="PF_p98_INBAR", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    inside_bar: bool = high < high[1] and low > low[1]
    bull_inside: bool = inside_bar and close > open
    bear_inside: bool = inside_bar and close < open

    if bull_inside and strategy.position_size <= 0:
        if strategy.position_size < 0:
            strategy.close('S', comment='flip flat')
        strategy.entry('L', strategy.long, comment='bull inside-bar')

    if bear_inside and strategy.position_size >= 0:
        if strategy.position_size > 0:
            strategy.close('L', comment='flip flat')
        strategy.entry('S', strategy.short, comment='bear inside-bar')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
