"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method
from pynecore.core.pine_udt import udt
from pynecore.lib import bar_index, close, color, input, na, plot, script, strategy, ta


@udt
class CourierEnvelope:
    center: float = na(float)
    width: float = na(float)
    createdAt: int = na(int)


@script.strategy("PineForge — Courier UDT Return Method", overlay=True, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=2, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    centerLength=input.int(37, "Envelope Center Length", minval=5, group="Envelope"),
    rangeLength=input.int(16, "Envelope Range Length", minval=2, group="Envelope"),
    entryMultiplier=input.float(1.15, "Entry Width", minval=0.1, step=0.05, group="Envelope"),
    maximumAtrLoss=input.float(2.4, "Maximum ATR Loss", minval=0.5, step=0.1, group="Risk")
):
    def buildEnvelope(source: float, centerLength: int, rangeLength: int):
        centerValue = ta.ema(source, centerLength)
        widthValue = ta.atr(rangeLength)
        return CourierEnvelope(centerValue, widthValue, bar_index)

    @method
    def upperGate(self: CourierEnvelope, multiplier: float):
        return self.center + self.width * multiplier

    activeEnvelope: CourierEnvelope = buildEnvelope(close, centerLength, rangeLength)
    upperBoundary = upperGate(activeEnvelope, entryMultiplier)
    ageIsValid = bar_index - activeEnvelope.createdAt == 0

    enterLong = ageIsValid and ta.crossover(close, upperBoundary)
    envelopeEnded = close < activeEnvelope.center
    riskExceeded = strategy.position_size > 0 and close < strategy.position_avg_price - activeEnvelope.width * maximumAtrLoss

    if strategy.position_size == 0 and enterLong:
        strategy.entry('Courier Long', strategy.long)
    elif strategy.position_size > 0 and (envelopeEnded or riskExceeded):
        strategy.close('Courier Long', comment='ATR risk' if riskExceeded else 'Envelope ended')

    plot(activeEnvelope.center, 'Envelope Center', color=color.orange)
    plot(upperBoundary, 'Envelope Gate', color=color.blue)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
