"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, script, strategy, ta


@script.strategy("PF OCA probe 02 - multi-bracket isolation", shorttitle="OCA_p02_MGP", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=2, pyramiding=1, process_orders_on_close=False)
def main():
    rsiVal = ta.rsi(close, 14)
    atrVal = ta.atr(14)
    emaFast = ta.ema(close, 9)
    emaSlow = ta.ema(close, 21)

    entryCond: bool = ta.crossover(emaFast, emaSlow) and rsiVal < 60

    if entryCond and strategy.position_size == 0:
        strategy.entry('L', strategy.long, qty=2, comment='entry')

    if strategy.position_size > 0:
        entry = strategy.position_avg_price

        strategy.exit('X_A', from_entry='L', qty=1, limit=entry + atrVal * 1.0, stop=entry - atrVal * 1.0, oca_name='GRP_A')

        strategy.exit('X_B', from_entry='L', qty=1, limit=entry + atrVal * 2.0, stop=entry - atrVal * 2.0, oca_name='GRP_B')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
