"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, script, strategy, ta, volume


@script.strategy("PF TA recompute probe 02 - untested classes", shorttitle="TArec_p02_UNT", overlay=True, initial_capital=1000000, use_bar_magnifier=True, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    almaVal = ta.alma(close, 14, 0.85, 6)
    sarVal = ta.sar(0.02, 0.02, 0.2)
    corrVal = ta.correlation(close, volume, 20)

    bullEntry: bool = ta.crossover(close, almaVal) and sarVal < close and (corrVal > 0.0)
    bearExit: bool = sarVal > close

    if bullEntry and strategy.position_size == 0:
        strategy.entry('L', strategy.long, qty=1, comment='entry long')
    if bearExit and strategy.position_size > 0:
        strategy.close('L', comment='exit long')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
