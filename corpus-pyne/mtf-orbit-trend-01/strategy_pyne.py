"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import barmerge, close, color, input, plot, request, script, strategy, syminfo, ta


@script.strategy("PineForge — Orbit MTF Trend", overlay=True, initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=6, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    higherTimeframe=input.timeframe("60", "Higher Timeframe", group="Signal"),
    higherLength=input.int(34, "Higher EMA", minval=3, group="Signal"),
    localLength=input.int(13, "Local EMA", minval=2, group="Signal"),
    atrLength=input.int(16, "ATR Length", minval=2, group="Risk"),
    stopAtr=input.float(2.2, "Stop ATR", minval=0.5, step=0.1, group="Risk")
):
    higherCenter = request.security(syminfo.tickerid, higherTimeframe, ta.ema(close, higherLength), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_off)

    localCenter = ta.ema(close, localLength)
    atrValue = ta.atr(atrLength)

    if ta.crossover(localCenter, higherCenter):
        strategy.entry('Orbit Long', strategy.long)
    if strategy.position_size > 0 and ta.crossunder(localCenter, higherCenter):
        strategy.close('Orbit Long', comment='Higher-timeframe trend changed')
    if strategy.position_size > 0:
        strategy.exit('Orbit Guard', from_entry='Orbit Long', stop=strategy.position_avg_price - atrValue * stopAtr)

    plot(higherCenter, 'Higher EMA', color=color.orange)
    plot(localCenter, 'Local EMA', color=color.aqua)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
