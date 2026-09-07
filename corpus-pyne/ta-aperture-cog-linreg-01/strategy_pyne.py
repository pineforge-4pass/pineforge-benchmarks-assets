"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, display, input, plot, script, strategy, ta


@script.strategy("PineForge — Aperture COG LinReg", overlay=True, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=2, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    cogLength=input.int(13, "COG Length", minval=3, group="Cycle"),
    cogSignalLength=input.int(7, "COG Signal Length", minval=2, group="Cycle"),
    regressionLength=input.int(38, "Regression Length", minval=5, group="Trend"),
    atrLength=input.int(20, "ATR Length", minval=2, group="Risk"),
    maximumAtrLoss=input.float(2.5, "Maximum ATR Loss", minval=0.5, step=0.1, group="Risk")
):
    cogValue = ta.cog(close, cogLength)
    cogSignal = ta.ema(cogValue, cogSignalLength)
    regressionNow = ta.linreg(close, regressionLength, 0)
    regressionPrior = ta.linreg(close, regressionLength, 1)
    atrValue = ta.atr(atrLength)
    regressionRising = regressionNow > regressionPrior

    enterLong = ta.crossover(cogValue, cogSignal) and regressionRising and (close > regressionNow)
    cycleEnded = ta.crossunder(cogValue, cogSignal) or not regressionRising
    riskExceeded = strategy.position_size > 0 and close < strategy.position_avg_price - atrValue * maximumAtrLoss

    if strategy.position_size == 0 and enterLong:
        strategy.entry('Aperture Long', strategy.long)
    elif strategy.position_size > 0 and (cycleEnded or riskExceeded):
        strategy.close('Aperture Long', comment='ATR risk' if riskExceeded else 'Cycle ended')

    plot(regressionNow, 'Regression Path', color=color.fuchsia)
    plot(cogValue, 'COG', color=color.teal, display=display.data_window)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
