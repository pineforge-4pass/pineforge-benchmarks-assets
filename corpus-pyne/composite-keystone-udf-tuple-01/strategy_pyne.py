"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, input, plot, script, strategy, ta


@script.strategy("PineForge — Keystone UDF Tuple", overlay=True, initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=7, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    channelLength=input.int(27, "Channel Length", minval=3, group="Signal"),
    widthMultiplier=input.float(1.6, "Channel Width ATR", minval=0.25, step=0.05, group="Signal"),
    targetMultiplier=input.float(2.1, "Target Widths", minval=0.5, step=0.1, group="Risk")
):
    def channel(source: float, length: int, widthMultiplier: float):
        basis: float = ta.ema(source, length)
        width: float = ta.atr(length) * widthMultiplier
        upper: float = basis + width
        lower: float = basis - width
        return (basis, upper, lower, width)

    basis, upperBand, lowerBand, channelWidth = channel(close, channelLength, widthMultiplier)

    if ta.crossover(close, upperBand):
        strategy.entry('Keystone Long', strategy.long)

    if ta.crossunder(close, basis):
        strategy.close('Keystone Long', comment='Return through basis')

    if strategy.position_size > 0:
        strategy.exit('Keystone Risk', from_entry='Keystone Long', stop=strategy.position_avg_price - channelWidth, limit=strategy.position_avg_price + channelWidth * targetMultiplier)

    plot(basis, 'Basis', color=color.gray)
    plot(upperBand, 'Upper', color=color.green)
    plot(lowerBand, 'Lower', color=color.red)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
