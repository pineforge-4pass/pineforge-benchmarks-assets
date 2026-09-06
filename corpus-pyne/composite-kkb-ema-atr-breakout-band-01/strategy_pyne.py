"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, input, script, strategy, ta


@script.strategy("PF probe kkb-probe-02-breakout-trigger", shorttitle="PF_kkb02_BRK", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_band_len=input.int(20, "Band EMA length", minval=2),
    i_atr_len=input.int(14, "ATR length", minval=2),
    i_atr_mult=input.float(1.5, "ATR multiplier", minval=0.1, step=0.1)
):

    band: float = ta.ema(close, i_band_len)
    vol: float = ta.atr(i_atr_len)
    upper: float = band + vol * i_atr_mult
    lower: float = band - vol * i_atr_mult

    cross_up: bool = ta.crossover(close, upper)
    cross_down: bool = ta.crossunder(close, lower)

    if cross_up and strategy.position_size <= 0:
        strategy.entry('L', strategy.long, qty=1, comment='band breakout long')

    if cross_down and strategy.position_size >= 0:
        strategy.entry('S', strategy.short, qty=1, comment='band breakdown short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
