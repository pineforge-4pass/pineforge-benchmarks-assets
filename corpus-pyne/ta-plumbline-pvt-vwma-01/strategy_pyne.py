"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, display, input, plot, script, strategy, ta
from pynecore.types import Series


@script.strategy("PineForge — Plumbline PVT VWMA", overlay=True, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=2, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    vwmaLength=input.int(33, "VWMA Length", minval=3, group="Trend"),
    pvtSignalLength=input.int(41, "PVT Signal Length", minval=3, group="Volume Flow"),
    atrLength=input.int(21, "ATR Length", minval=2, group="Risk"),
    maximumAtrLoss=input.float(2.2, "Maximum ATR Loss", minval=0.5, step=0.1, group="Risk")
):
    volumeWeightedCenter = ta.vwma(close, vwmaLength)
    priceVolumeTrend = ta.pvt
    pvtSignal = ta.ema(priceVolumeTrend, pvtSignalLength)
    atrValue = ta.atr(atrLength)

    confirmedTrend: Series = close > volumeWeightedCenter and priceVolumeTrend > pvtSignal
    enterLong = confirmedTrend and (not confirmedTrend[1])
    trendEnded = close < volumeWeightedCenter or priceVolumeTrend < pvtSignal
    riskExceeded = strategy.position_size > 0 and close < strategy.position_avg_price - atrValue * maximumAtrLoss

    if strategy.position_size == 0 and enterLong:
        strategy.entry('Plumbline Long', strategy.long)
    elif strategy.position_size > 0 and (trendEnded or riskExceeded):
        strategy.close('Plumbline Long', comment='ATR risk' if riskExceeded else 'Weighted trend')

    plot(volumeWeightedCenter, 'Volume-Weighted Center', color=color.teal)
    plot(priceVolumeTrend - pvtSignal, 'PVT Distance', color=color.blue, display=display.data_window)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
