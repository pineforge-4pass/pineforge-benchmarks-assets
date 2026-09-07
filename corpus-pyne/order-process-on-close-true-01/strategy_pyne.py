"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, script, strategy, ta


@script.strategy("PF process-orders 02 - on_close=true", shorttitle="POC_p02_TRUE", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=True)
def main():
    rsiVal = ta.rsi(close, 14)
    emaFast = ta.ema(close, 9)
    emaSlow = ta.ema(close, 21)

    entryCond: bool = ta.crossover(emaFast, emaSlow) and rsiVal < 70
    exitCond: bool = ta.crossunder(emaFast, emaSlow)

    if entryCond and strategy.position_size == 0:
        strategy.entry('L', strategy.long, qty=1, comment='entry')
    if exitCond and strategy.position_size > 0:
        strategy.close('L', comment='exit')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
