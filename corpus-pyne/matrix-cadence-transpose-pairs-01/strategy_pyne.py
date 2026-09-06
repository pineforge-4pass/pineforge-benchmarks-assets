"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_method import method_call
from pynecore.lib import close, color, display, input, matrix, plot, script, strategy, ta, volume
from pynecore.types import Matrix, Persistent, Series


@script.strategy("PineForge — Cadence Matrix Pairing", overlay=True, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=2, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    shortHorizon=input.int(6, "Short Horizon", minval=2, group="Pair Grid"),
    mediumHorizon=input.int(18, "Medium Horizon", minval=3, group="Pair Grid"),
    longHorizon=input.int(54, "Long Horizon", minval=5, group="Pair Grid"),
    requiredPairs=input.int(2, "Required Confirmed Pairs", minval=1, maxval=3, group="Pair Grid"),
    trendLength=input.int(43, "Trend EMA Length", minval=5, group="Trend"),
    atrLength=input.int(16, "ATR Length", minval=2, group="Risk"),
    maximumAtrLoss=input.float(2.4, "Maximum ATR Loss", minval=0.5, step=0.1, group="Risk")
):
    shortPriceUp = 1.0 if close > close[shortHorizon] else 0.0
    mediumPriceUp = 1.0 if close > close[mediumHorizon] else 0.0
    longPriceUp = 1.0 if close > close[longHorizon] else 0.0
    shortVolumeFirm = 1.0 if volume > ta.sma(volume, shortHorizon) else 0.0
    mediumVolumeFirm = 1.0 if volume > ta.sma(volume, mediumHorizon) else 0.0
    longVolumeFirm = 1.0 if volume > ta.sma(volume, longHorizon) else 0.0

    factorRows: Persistent[Matrix[float]] = matrix.new(2, 3, 0.0)
    matrix.set(factorRows, 0, 0, shortPriceUp)
    matrix.set(factorRows, 0, 1, mediumPriceUp)
    matrix.set(factorRows, 0, 2, longPriceUp)
    matrix.set(factorRows, 1, 0, shortVolumeFirm)
    matrix.set(factorRows, 1, 1, mediumVolumeFirm)
    matrix.set(factorRows, 1, 2, longVolumeFirm)
    horizonPairs = matrix.transpose(factorRows)

    confirmedPairs: int = 0
    for horizonIndex in pine_range(0, 2):
        priceVote = method_call('get', horizonPairs, horizonIndex, 0)
        volumeVote = method_call('get', horizonPairs, horizonIndex, 1)
        if priceVote == 1.0 and volumeVote == 1.0:
            confirmedPairs += 1

    trendLine = ta.ema(close, trendLength)
    atrValue = ta.atr(atrLength)
    consensusReady: Series = confirmedPairs >= requiredPairs

    enterLong = consensusReady and (not consensusReady[1]) and (close > trendLine)
    consensusEnded = confirmedPairs == 0 or close < trendLine
    riskExceeded = strategy.position_size > 0 and close < strategy.position_avg_price - atrValue * maximumAtrLoss

    if strategy.position_size == 0 and enterLong:
        strategy.entry('Cadence Long', strategy.long)
    elif strategy.position_size > 0 and (consensusEnded or riskExceeded):
        strategy.close('Cadence Long', comment='ATR risk' if riskExceeded else 'Pair consensus')

    plot(trendLine, 'Trend EMA', color=color.orange)
    plot(confirmedPairs, 'Confirmed Horizon Pairs', color=color.blue, display=display.data_window)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
