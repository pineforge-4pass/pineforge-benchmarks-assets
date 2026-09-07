"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method
from pynecore.core.pine_udt import udt
from pynecore.lib import close, color, input, na, plot, script, strategy, ta


@udt
class Tessellation:
    center: float = na(float)
    span: float = na(float)


@script.strategy("PineForge — Tessellate UDT Tuple Method", overlay=True, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=2, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    centerLength=input.int(42, "Center EMA Length", minval=5, group="Channel"),
    spanLength=input.int(17, "ATR Span Length", minval=2, group="Channel"),
    upperScale=input.float(1.25, "Upper Span", minval=0.1, step=0.05, group="Channel"),
    lowerScale=input.float(0.8, "Lower Span", minval=0.1, step=0.05, group="Channel"),
    maximumAtrLoss=input.float(2.5, "Maximum ATR Loss", minval=0.5, step=0.1, group="Risk")
):
    @method
    def boundaries(self: Tessellation, upperScale: float, lowerScale: float):
        upperBoundary = self.center + self.span * upperScale
        lowerBoundary = self.center - self.span * lowerScale
        return (upperBoundary, lowerBoundary)

    tile: Tessellation = Tessellation(ta.ema(close, centerLength), ta.atr(spanLength))
    upperBoundary, lowerBoundary = boundaries(tile, upperScale, lowerScale)

    enterLong = ta.crossover(close, upperBoundary)
    channelEnded = close < lowerBoundary
    riskExceeded = strategy.position_size > 0 and close < strategy.position_avg_price - tile.span * maximumAtrLoss

    if strategy.position_size == 0 and enterLong:
        strategy.entry('Tessellate Long', strategy.long)
    elif strategy.position_size > 0 and (channelEnded or riskExceeded):
        strategy.close('Tessellate Long', comment='ATR risk' if riskExceeded else 'Channel ended')

    plot(tile.center, 'Tile Center', color=color.orange)
    plot(upperBoundary, 'Upper Boundary', color=color.green)
    plot(lowerBoundary, 'Lower Boundary', color=color.red)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
