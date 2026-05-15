"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, currency, input, plot, script, strategy, ta
from pynecore.types import Series


@script.strategy("Multi Indicator Score", overlay=True, initial_capital=1000000, currency=currency.USD, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    rsiLen=input.int(14, "RSI Length", minval=1),
    maLen=input.int(20, "MA Length", minval=1),
    bbLen=input.int(20, "BB Length", minval=5),
    bbMult=input.float(2.0, "BB Mult", step=0.1)
):

    rsiVal = ta.rsi(close, rsiLen)
    emaVal = ta.ema(close, maLen)
    bbMid, bbUpper, bbLower = ta.bb(close, bbLen, bbMult)
    atrVal = ta.atr(14)

    score: Series[int] = 0

    if rsiVal > 50:
        score += 1
    elif rsiVal < 50:
        score -= 1

    if close > emaVal:
        score += 1
    else:
        score -= 1

    if close > bbMid:
        score += 1
    else:
        score -= 1

    longCond = score >= 2 and score[1] < 2
    shortCond = score <= -2 and score[1] > -2

    if longCond:
        strategy.entry('Long', strategy.long)
    if shortCond:
        strategy.entry('Short', strategy.short)

    if strategy.position_size > 0 and score <= 0:
        strategy.close('Long')
    if strategy.position_size < 0 and score >= 0:
        strategy.close('Short')

    plot(emaVal, 'EMA', color=color.blue)
    plot(bbUpper, 'BB Upper', color=color.gray)
    plot(bbLower, 'BB Lower', color=color.gray)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)