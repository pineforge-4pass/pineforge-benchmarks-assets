"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, dayofweek, input, plot, script, strategy, ta
from pynecore.types import Series


@script.strategy("PineForge — Waypoint Weekday MACD", overlay=False, initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=6, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    fastLength=input.int(12, "MACD Fast", minval=2, group="Signal"),
    slowLength=input.int(26, "MACD Slow", minval=3, group="Signal"),
    signalLength=input.int(9, "MACD Signal", minval=2, group="Signal"),
    tradeWeekends=input.bool(False, "Trade Weekends", group="Calendar"),
    allowShort=input.bool(True, "Allow Short", group="Execution"),
    atrLength=input.int(14, "ATR Length", minval=2, group="Risk"),
    stopAtr=input.float(2.1, "Stop ATR", minval=0.5, step=0.1, group="Risk")
):
    macdLine, signalLine, macdHistogram = ta.macd(close, fastLength, slowLength, signalLength)
    atrValue = ta.atr(atrLength)

    weekday = dayofweek >= dayofweek.monday and dayofweek <= dayofweek.friday
    calendarAllowed: Series = tradeWeekends or weekday
    calendarClosed = not calendarAllowed and calendarAllowed[1]

    if calendarAllowed and ta.crossover(macdLine, signalLine):
        strategy.entry('Waypoint Long', strategy.long)

    if calendarAllowed and allowShort and ta.crossunder(macdLine, signalLine):
        strategy.entry('Waypoint Short', strategy.short)

    if calendarClosed:
        strategy.close('Waypoint Long', comment='Weekday window closed')
        strategy.close('Waypoint Short', comment='Weekday window closed')

    if strategy.position_size > 0:
        strategy.exit('Waypoint Long Guard', from_entry='Waypoint Long', stop=strategy.position_avg_price - atrValue * stopAtr)

    if strategy.position_size < 0:
        strategy.exit('Waypoint Short Guard', from_entry='Waypoint Short', stop=strategy.position_avg_price + atrValue * stopAtr)

    plot(macdLine, 'MACD', color=color.blue)
    plot(signalLine, 'Signal', color=color.orange)
    plot(macdHistogram, 'Histogram', color=color.green if macdHistogram >= 0 else color.red, style=plot.style_columns)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
