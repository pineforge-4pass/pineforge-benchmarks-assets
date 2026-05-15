"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, currency, high, open, script, strategy, ta


@script.strategy("PF magnifier dist probe 01-endpoints ENDPOINTS", shorttitle="MAG_END", overlay=True, initial_capital=1000000, currency=currency.USD, use_bar_magnifier=True, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    emaFast = ta.ema(close, 9)
    emaSlow = ta.ema(close, 21)

    entryCond: bool = ta.crossover(emaFast, emaSlow)
    exitCond: bool = ta.crossunder(emaFast, emaSlow)

    if entryCond and strategy.position_size == 0:
        strategy.entry('L', strategy.long, qty=1, comment='entry long')
        stopLvl: float = open + (high - open) * 0.5
        strategy.exit('X', from_entry='L', stop=stopLvl, comment='mid-bar stop')

    if exitCond and strategy.position_size > 0:
        strategy.close('L', comment='exit long')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
