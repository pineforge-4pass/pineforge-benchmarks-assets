"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import bgcolor, close, color, input, na, script, strategy, ta, time, timeframe
from pynecore.types import Series


@script.strategy("PineForge — Compass Session Market", overlay=True, initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=7, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    tradeSession=input.session("0800-1600", "Trade Session", group="Session"),
    tradeTimezone=input.string("Etc/UTC", "Session Timezone", group="Session"),
    fastLength=input.int(16, "Fast EMA", minval=2, group="Signal"),
    slowLength=input.int(44, "Slow EMA", minval=3, group="Signal"),
    atrLength=input.int(14, "ATR Length", minval=2, group="Risk"),
    stopAtr=input.float(2.0, "Stop ATR", minval=0.5, step=0.1, group="Risk")
):
    insideSession: Series = not na(time(timeframe.period, tradeSession, tradeTimezone))
    wasInside = insideSession[1]
    sessionOpened = insideSession and (not wasInside)
    sessionClosed = not insideSession and wasInside

    fastEma = ta.ema(close, fastLength)
    slowEma = ta.ema(close, slowLength)
    atrValue = ta.atr(atrLength)

    if insideSession and (sessionOpened or ta.crossover(fastEma, slowEma)):
        strategy.entry('Compass Long', strategy.long)

    if sessionClosed:
        strategy.close('Compass Long', comment='Session flatten')

    if strategy.position_size > 0:
        strategy.exit('Compass Guard', from_entry='Compass Long', stop=strategy.position_avg_price - atrValue * stopAtr)

    bgcolor(color.new(color.blue, 90) if insideSession else na)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
