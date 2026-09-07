"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, high, input, low, script, strategy, ta


@script.strategy("PF probe 103 - stoch slow cross", shorttitle="PF_p103_STO", overlay=False, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_k_len=input.int(14, "Stoch %K length", minval=1, maxval=100),
    i_smooth=input.int(3, "Slow %K smoothing", minval=1, maxval=20),
    i_d_len=input.int(3, "%D smoothing", minval=1, maxval=20)
):

    raw_k: float = ta.stoch(close, high, low, i_k_len)
    slow_k: float = ta.sma(raw_k, i_smooth)
    slow_d: float = ta.sma(slow_k, i_d_len)

    bull_cross: bool = ta.crossover(slow_k, slow_d) and slow_k < 80
    bear_cross: bool = ta.crossunder(slow_k, slow_d) and slow_k > 20

    if bull_cross:
        strategy.entry('L', strategy.long, comment='slowK cross above D')

    if bear_cross:
        strategy.entry('S', strategy.short, comment='slowK cross below D')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
