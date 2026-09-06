"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import barstate, close, color, display, input, map, plot, script, strategy, ta
from pynecore.types import Persistent


@script.strategy("PineForge — Archive Map Presence", overlay=True, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=2, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    regimeChoice=input.string("balanced", "Regime Key", options=("patient", "balanced", "responsive", "unknown"), group="Configuration"),
    fallbackRsi=input.float(63.0, "Fallback RSI", minval=40, maxval=80, step=0.5, group="Configuration"),
    trendLength=input.int(46, "Trend EMA Length", minval=5, group="Trend"),
    atrLength=input.int(18, "ATR Length", minval=2, group="Risk"),
    maximumAtrLoss=input.float(2.3, "Maximum ATR Loss", minval=0.5, step=0.1, group="Risk")
):
    thresholdArchive: Persistent[dict[str, float]] = map.new()
    if barstate.isfirst:
        map.put(thresholdArchive, 'patient', 61.5)
        map.put(thresholdArchive, 'balanced', 56.5)
        map.put(thresholdArchive, 'responsive', 52.0)

    hasRequestedRegime = map.contains(thresholdArchive, regimeChoice)
    entryRsi = map.get(thresholdArchive, regimeChoice) if hasRequestedRegime else fallbackRsi
    rsiValue = ta.rsi(close, 15)
    trendLine = ta.ema(close, trendLength)
    atrValue = ta.atr(atrLength)

    enterLong = hasRequestedRegime and ta.crossover(rsiValue, entryRsi) and (close > trendLine)
    regimeEnded = rsiValue < entryRsi - 9 or close < trendLine
    riskExceeded = strategy.position_size > 0 and close < strategy.position_avg_price - atrValue * maximumAtrLoss

    if strategy.position_size == 0 and enterLong:
        strategy.entry('Archive Long', strategy.long)
    elif strategy.position_size > 0 and (regimeEnded or riskExceeded):
        strategy.close('Archive Long', comment='ATR risk' if riskExceeded else 'Archive regime')

    plot(trendLine, 'Trend EMA', color=color.orange)
    plot(entryRsi, 'Selected RSI', color=color.purple, display=display.data_window)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
