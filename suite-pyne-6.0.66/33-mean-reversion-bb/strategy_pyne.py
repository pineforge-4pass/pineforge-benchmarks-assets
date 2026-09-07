"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, currency, input, plot, script, strategy, ta


@script.strategy("Mean Reversion Bollinger", overlay=True, initial_capital=1000000, currency=currency.USD, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    bbLen=input.int(20, "BB Length", minval=5),
    bbMult=input.float(2.0, "BB Multiplier", step=0.1),
    rsiLen=input.int(14, "RSI Length", minval=1),
    rsiOB=input.int(70, "RSI Overbought"),
    rsiOS=input.int(30, "RSI Oversold")
):

    bbMid, bbUpper, bbLower = ta.bb(close, bbLen, bbMult)
    rsiVal = ta.rsi(close, rsiLen)

    longCond = close < bbLower and rsiVal < rsiOS
    shortCond = close > bbUpper and rsiVal > rsiOB

    if longCond:
        strategy.entry('Long', strategy.long)
    if shortCond:
        strategy.entry('Short', strategy.short)

    if strategy.position_size > 0 and close > bbMid:
        strategy.close('Long')
    if strategy.position_size < 0 and close < bbMid:
        strategy.close('Short')

    plot(bbUpper, 'Upper', color=color.red)
    plot(bbMid, 'Mid', color=color.gray)
    plot(bbLower, 'Lower', color=color.green)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
