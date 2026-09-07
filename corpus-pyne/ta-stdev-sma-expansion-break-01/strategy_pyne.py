"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, input, script, strategy, ta


@script.strategy("PF probe 105 - volty expansion close", shorttitle="PF_p105_VEXP", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_len=input.int(20, "Baseline / stdev length", minval=2, maxval=200),
    i_mult=input.float(2.0, "Expansion multiple", minval=0.5, maxval=10.0, step=0.1)
):

    baseline: float = ta.sma(close, i_len)
    vol: float = ta.stdev(close, i_len)
    upper: float = baseline + vol * i_mult
    lower: float = baseline - vol * i_mult

    bull_break: bool = close > upper
    bear_break: bool = close < lower

    if bull_break and strategy.position_size <= 0:
        if strategy.position_size < 0:
            strategy.close('S', comment='flip flat')
        strategy.entry('L', strategy.long, comment='upper-band break')

    if bear_break and strategy.position_size >= 0:
        if strategy.position_size > 0:
            strategy.close('L', comment='flip flat')
        strategy.entry('S', strategy.short, comment='lower-band break')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
