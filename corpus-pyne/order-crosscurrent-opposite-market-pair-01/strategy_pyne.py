"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, display, input, plot, script, strategy, ta


@script.strategy("PineForge — Crosscurrent Market Pair", overlay=True, initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=8, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    rsiLength=input.int(17, "RSI Length", minval=2, group="Signal"),
    upperTurn=input.float(58.0, "Bull Threshold", minval=50, maxval=90, group="Signal"),
    lowerTurn=input.float(42.0, "Bear Threshold", minval=10, maxval=50, group="Signal"),
    atrLength=input.int(14, "ATR Length", minval=2, group="Risk"),
    stopAtr=input.float(2.4, "Stop ATR", minval=0.5, step=0.1, group="Risk")
):
    rsiValue = ta.rsi(close, rsiLength)
    atrValue = ta.atr(atrLength)
    bullTurn = ta.crossover(rsiValue, upperTurn)
    bearTurn = ta.crossunder(rsiValue, lowerTurn)

    if bullTurn:
        if strategy.position_size < 0:
            strategy.close('Crosscurrent Short', comment='Close before opposite market entry')
        strategy.entry('Crosscurrent Long', strategy.long)

    if bearTurn:
        if strategy.position_size > 0:
            strategy.close('Crosscurrent Long', comment='Close before opposite market entry')
        strategy.entry('Crosscurrent Short', strategy.short)

    if strategy.position_size > 0:
        strategy.exit('Crosscurrent Long Guard', from_entry='Crosscurrent Long', stop=strategy.position_avg_price - atrValue * stopAtr)

    if strategy.position_size < 0:
        strategy.exit('Crosscurrent Short Guard', from_entry='Crosscurrent Short', stop=strategy.position_avg_price + atrValue * stopAtr)

    plot(rsiValue, 'RSI', display=display.data_window)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
