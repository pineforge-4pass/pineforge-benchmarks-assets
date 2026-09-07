"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, input, script, strategy, string, ta


@script.strategy("Regex String Filter", overlay=False, initial_capital=1000000, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    rules=input.string("MACD=LONG,RSI>50", "Rule Set")
):
    lrules = string.lower(rules)
    useRsi: bool = False
    useMacd: bool = False

    if string.match(lrules, 'rsi>50') != '':
        useRsi = True
    if string.match(lrules, 'macd=long') != '':
        useMacd = True

    rsiVal = ta.rsi(close, 14)
    macdLine, sigLine, _ = ta.macd(close, 12, 26, 9)

    longCond: bool = True
    if useRsi and rsiVal <= 50:
        longCond = False
    if useMacd and macdLine <= sigLine:
        longCond = False

    if longCond:
        strategy.entry('Long', strategy.long)
    else:
        strategy.close('Long')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
