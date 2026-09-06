"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, input, na, plot, script, strategy, ta, time, timeframe


@script.strategy("PineForge — Gatekeeper Risk Cap", overlay=True, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=2, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=True, calc_on_order_fills=False)
def main(
    tradeSession=input.session("0900-1700", "Trade Session", group="Session"),
    sessionTimezone=input.string("Asia/Taipei", "Session Timezone", group="Session"),
    maxDailyFills=input.int(4, "Maximum Daily Filled Orders", minval=1, maxval=20, group="Risk"),
    fastLength=input.int(10, "Fast EMA", minval=2, group="Signal"),
    slowLength=input.int(31, "Slow EMA", minval=3, group="Signal"),
    atrLength=input.int(14, "ATR Length", minval=2, group="Risk"),
    stopAtr=input.float(1.8, "Stop ATR", minval=0.5, step=0.1, group="Risk")
):
    strategy.risk.max_intraday_filled_orders(maxDailyFills)
    newDay = timeframe.change('1D')
    inSession = not na(time(timeframe.period, tradeSession, sessionTimezone))
    fastEma = ta.ema(close, fastLength)
    slowEma = ta.ema(close, slowLength)
    atrValue = ta.atr(atrLength)

    if inSession and ta.crossover(fastEma, slowEma):
        strategy.entry('Gatekeeper Long', strategy.long)
    if strategy.position_size > 0 and (not inSession or newDay):
        strategy.close('Gatekeeper Long', comment='Session boundary')
    if strategy.position_size > 0:
        strategy.exit('Gatekeeper Guard', from_entry='Gatekeeper Long', stop=strategy.position_avg_price - atrValue * stopAtr)

    plot(fastEma, 'Fast EMA', color=color.green)
    plot(slowEma, 'Slow EMA', color=color.red)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
