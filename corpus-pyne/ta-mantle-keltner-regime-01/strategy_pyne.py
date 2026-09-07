"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, input, plot, script, strategy, ta


@script.strategy("PineForge — Mantle Keltner Regime", overlay=True, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=2, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    channelLength=input.int(24, "Keltner Length", minval=3, group="Channel"),
    channelMultiplier=input.float(1.7, "Keltner Multiplier", minval=0.2, step=0.1, group="Channel"),
    trendLength=input.int(57, "Trend EMA Length", minval=5, group="Trend"),
    maximumChannelLoss=input.float(0.65, "Maximum Channel Loss", minval=0.1, maxval=2.0, step=0.05, group="Risk")
):
    channelCenter, channelUpper, channelLower = ta.kc(close, channelLength, channelMultiplier)
    trendLine = ta.ema(close, trendLength)
    channelWidth = channelUpper - channelLower

    enterLong = ta.crossover(close, channelUpper) and channelCenter > trendLine
    regimeEnded = close < channelCenter
    riskExceeded = strategy.position_size > 0 and close < strategy.position_avg_price - channelWidth * maximumChannelLoss

    if strategy.position_size == 0 and enterLong:
        strategy.entry('Mantle Long', strategy.long)
    elif strategy.position_size > 0 and (regimeEnded or riskExceeded):
        strategy.close('Mantle Long', comment='Channel risk' if riskExceeded else 'Channel regime')

    plot(channelCenter, 'Keltner Center', color=color.gray)
    plot(channelUpper, 'Keltner Upper', color=color.green)
    plot(channelLower, 'Keltner Lower', color=color.red)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
