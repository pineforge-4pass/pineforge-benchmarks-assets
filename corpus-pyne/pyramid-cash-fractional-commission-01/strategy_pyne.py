"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, hour, minute, script, strategy, ta


@script.strategy("PF Pyramid carry 02 - cash fractional", shorttitle="PYR_p02_CASH", overlay=True, initial_capital=1000000, commission_type=strategy.commission.cash_per_contract, commission_value=0.05, slippage=0, default_qty_type=strategy.cash, default_qty_value=50000, pyramiding=3, process_orders_on_close=False)
def main():
    rsiVal = ta.rsi(close, 14)
    emaFast = ta.ema(close, 9)
    emaSlow = ta.ema(close, 21)

    entryCond: bool = ta.crossover(emaFast, emaSlow) and rsiVal > 40 and (rsiVal < 70)

    if entryCond:
        strategy.entry('L', strategy.long, comment='cash add')

    if hour == 23 and minute == 45:
        strategy.close_all(comment='session close')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
