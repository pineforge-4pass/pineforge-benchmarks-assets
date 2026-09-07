"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bgcolor, close, color, input, na, plot, script, strategy, ta, time,
    timeframe
)
from pynecore.types import Series


@script.strategy("PineForge — Borough New York Session", overlay=True, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=2, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    sessionWindow=input.session("0930-1600", "New York Session", group="Session"),
    trendLength=input.int(38, "Trend EMA Length", minval=5, group="Signal"),
    minimumRsi=input.float(52.0, "Minimum RSI", minval=20, maxval=80, step=1, group="Signal")
):
    sessionStamp: Series = time(timeframe.period, sessionWindow, 'America/New_York')
    inSession = not na(sessionStamp)
    wasInSession = not na(sessionStamp[1])
    sessionOpened = inSession and (not wasInSession)
    sessionClosed = wasInSession and (not inSession)

    trendLine = ta.ema(close, trendLength)
    rsiValue = ta.rsi(close, 14)
    eligibleOpen = sessionOpened and close > trendLine and (rsiValue > minimumRsi)

    if strategy.position_size == 0 and eligibleOpen:
        strategy.entry('Borough Long', strategy.long)
    elif strategy.position_size > 0 and sessionClosed:
        strategy.close('Borough Long', comment='New York session ended')

    plot(trendLine, 'Trend EMA', color=color.orange)
    bgcolor(color.new(color.blue, 92) if inSession else na, title='New York Session')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
