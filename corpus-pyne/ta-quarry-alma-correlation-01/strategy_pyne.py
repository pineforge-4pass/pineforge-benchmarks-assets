"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, display, input, plot, script, strategy, ta, volume


@script.strategy("PineForge — Quarry ALMA Correlation", overlay=True, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=2, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    almaLength=input.int(31, "ALMA Length", minval=5, group="Signal"),
    almaOffset=input.float(0.72, "ALMA Offset", minval=0.05, maxval=0.95, step=0.01, group="Signal"),
    almaSigma=input.float(5.4, "ALMA Sigma", minval=1.0, maxval=12.0, step=0.1, group="Signal"),
    correlationLength=input.int(23, "Correlation Length", minval=5, group="Confirmation"),
    minimumCorrelation=input.float(0.04, "Minimum Correlation", minval=-0.8, maxval=0.8, step=0.01, group="Confirmation"),
    atrLength=input.int(17, "ATR Length", minval=2, group="Risk"),
    maximumAtrLoss=input.float(2.6, "Maximum ATR Loss", minval=0.5, step=0.1, group="Risk")
):
    almaLine = ta.alma(close, almaLength, almaOffset, almaSigma)
    priceVolumeCorrelation = ta.correlation(close, volume, correlationLength)
    atrValue = ta.atr(atrLength)

    enterLong = ta.crossover(close, almaLine) and priceVolumeCorrelation > minimumCorrelation
    regimeEnded = ta.crossunder(close, almaLine) or priceVolumeCorrelation < -minimumCorrelation
    riskExceeded = strategy.position_size > 0 and close < strategy.position_avg_price - atrValue * maximumAtrLoss

    if strategy.position_size == 0 and enterLong:
        strategy.entry('Quarry Long', strategy.long)
    elif strategy.position_size > 0 and (regimeEnded or riskExceeded):
        strategy.close('Quarry Long', comment='ATR risk' if riskExceeded else 'Correlation regime')

    plot(almaLine, 'ALMA Center', color=color.orange)
    plot(priceVolumeCorrelation, 'Price-Volume Correlation', color=color.teal, display=display.data_window)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
