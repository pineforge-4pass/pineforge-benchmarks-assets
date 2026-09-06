"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import barmerge, close, color, input, plot, request, script, strategy, syminfo, ta


@script.strategy("PineForge — Cascade MTF Tuple", overlay=True, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=2, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    higherTimeframe=input.timeframe("240", "Higher Timeframe", group="Signal"),
    centerLength=input.int(27, "Higher EMA", minval=3, group="Signal"),
    atrLength=input.int(15, "Higher ATR", minval=2, group="Signal"),
    entryDistance=input.float(0.35, "Entry Distance ATR", minval=0, step=0.05, group="Signal"),
    stopAtr=input.float(2.0, "Stop Higher ATR", minval=0.5, step=0.1, group="Risk")
):
    higherCenter, higherAtr = request.security(syminfo.tickerid, higherTimeframe, (ta.ema(close, centerLength), ta.atr(atrLength)), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_off)

    entryLine = higherCenter + higherAtr * entryDistance

    if ta.crossover(close, entryLine):
        strategy.entry('Cascade Long', strategy.long)
    if strategy.position_size > 0 and close < higherCenter:
        strategy.close('Cascade Long', comment='Higher center lost')
    if strategy.position_size > 0:
        strategy.exit('Cascade Guard', from_entry='Cascade Long', stop=strategy.position_avg_price - higherAtr * stopAtr)

    plot(higherCenter, 'Higher Center', color=color.blue)
    plot(entryLine, 'Tuple Entry Line', color=color.green)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
