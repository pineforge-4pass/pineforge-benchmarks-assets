"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, high, open, script, strategy, ta


@script.strategy("PF magnifier dist probe 08a - ENDPOINTS RSI cross", shorttitle="MAG_08a_END", overlay=True, initial_capital=1000000, use_bar_magnifier=True, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    rsiVal = ta.rsi(close, 14)
    entryCond: bool = ta.crossover(rsiVal, 50.0)
    exitCond: bool = ta.crossunder(rsiVal, 50.0)

    if entryCond and strategy.position_size == 0:
        strategy.entry('L', strategy.long, qty=1, comment='entry long')
        stopLvl: float = (open + high) * 0.5
        strategy.exit('X', from_entry='L', stop=stopLvl, comment='mid-bar stop')

    if exitCond and strategy.position_size > 0:
        strategy.close('L', comment='exit long')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
