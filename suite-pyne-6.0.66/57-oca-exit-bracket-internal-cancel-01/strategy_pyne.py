"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, currency, script, strategy, ta


@script.strategy("PF OCA probe 01 - exit bracket cancel", shorttitle="OCA_p01_3WAY", overlay=True, initial_capital=1000000, currency=currency.USD, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    rsiVal = ta.rsi(close, 14)
    atrVal = ta.atr(14)

    entryCond: bool = ta.crossover(rsiVal, 30)

    if entryCond and strategy.position_size == 0:
        strategy.entry('L', strategy.long, qty=1, comment='entry')

    if strategy.position_size > 0:
        entry = strategy.position_avg_price
        strategy.exit('X', from_entry='L', qty=1, limit=entry + atrVal * 1.5, stop=entry - atrVal * 1.5, oca_name='GRP')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
