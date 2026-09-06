"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    array, close, color, display, input, math, matrix, na, nz, plot, script,
    strategy, ta, volume
)
from pynecore.types import Matrix, Persistent


@script.strategy("PineForge — Eigen Matrix Covariance", overlay=True, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=2, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    covarianceLength=input.int(26, "Covariance Length", minval=5, group="Factors"),
    trendLength=input.int(58, "Trend EMA Length", minval=5, group="Trend"),
    minimumConcentration=input.float(1.28, "Minimum Principal Eigenvalue", minval=1.0, maxval=2.0, step=0.01, group="Factors"),
    atrLength=input.int(19, "ATR Length", minval=2, group="Risk"),
    maximumAtrLoss=input.float(2.6, "Maximum ATR Loss", minval=0.5, step=0.1, group="Risk")
):
    priceReturn = ta.roc(close, 1)
    volumeReturn = ta.roc(volume, 1)
    factorCorrelation = ta.correlation(priceReturn, volumeReturn, covarianceLength)
    safeCorrelation = nz(factorCorrelation, 0.0)

    correlationMatrix: Persistent[Matrix[float]] = matrix.new(2, 2, 0.0)
    matrix.set(correlationMatrix, 0, 0, 1.0)
    matrix.set(correlationMatrix, 0, 1, safeCorrelation)
    matrix.set(correlationMatrix, 1, 0, safeCorrelation)
    matrix.set(correlationMatrix, 1, 1, 1.0)

    eigenValues = matrix.eigenvalues(correlationMatrix)
    firstEigenvalue = array.get(eigenValues, 0) if array.size(eigenValues) > 0 else na
    secondEigenvalue = array.get(eigenValues, 1) if array.size(eigenValues) > 1 else na
    principalEigenvalue = math.max(firstEigenvalue, secondEigenvalue)
    trendLine = ta.ema(close, trendLength)
    atrValue = ta.atr(atrLength)

    enterLong = not na(principalEigenvalue) and ta.crossover(principalEigenvalue, minimumConcentration) and (close > trendLine)
    regimeEnded = principalEigenvalue < 1.08 or close < trendLine
    riskExceeded = strategy.position_size > 0 and close < strategy.position_avg_price - atrValue * maximumAtrLoss

    if strategy.position_size == 0 and enterLong:
        strategy.entry('Eigen Long', strategy.long)
    elif strategy.position_size > 0 and (regimeEnded or riskExceeded):
        strategy.close('Eigen Long', comment='ATR risk' if riskExceeded else 'Eigen regime')

    plot(trendLine, 'Trend EMA', color=color.orange)
    plot(principalEigenvalue, 'Principal Eigenvalue', color=color.purple, display=display.data_window)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
