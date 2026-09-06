"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, input, script, strategy, ta
from pynecore.types import Series


@script.strategy("VCP probe 03 - rsi smooth divergence", shorttitle="VCP_p03", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_rsi=input.int(14, "RSI Length", minval=5, maxval=30)
):

    rsiValue: float = ta.rsi(close, i_rsi)
    rsiSmooth: Series[float] = ta.ema(rsiValue, 3)

    rsiDivBull: bool = rsiSmooth < 40 and close > close[5] and (rsiSmooth > rsiSmooth[5])
    rsiDivBear: bool = rsiSmooth > 60 and close < close[5] and (rsiSmooth < rsiSmooth[5])

    if rsiDivBull and strategy.position_size == 0:
        strategy.entry('L', strategy.long, qty=1, comment='rsi div bull')

    if rsiDivBear and strategy.position_size > 0:
        strategy.close('L', comment='rsi div bear exit')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
