"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, display, input, plot, script, strategy, ta
from pynecore.types import Series


@script.strategy("PineForge — Conduit OBV AccDist", overlay=True, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=2, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    obvSignalLength=input.int(29, "OBV Signal Length", minval=3, group="Volume Flow"),
    accDistSignalLength=input.int(37, "AccDist Signal Length", minval=3, group="Volume Flow"),
    priceFilterLength=input.int(52, "Price Filter Length", minval=5, group="Trend"),
    atrLength=input.int(16, "ATR Length", minval=2, group="Risk"),
    maximumAtrLoss=input.float(2.4, "Maximum ATR Loss", minval=0.5, step=0.1, group="Risk")
):
    obvValue = ta.obv
    accDistValue = ta.accdist
    obvSignal = ta.ema(obvValue, obvSignalLength)
    accDistSignal = ta.ema(accDistValue, accDistSignalLength)
    priceFilter = ta.ema(close, priceFilterLength)
    atrValue = ta.atr(atrLength)

    flowAgreement: Series = obvValue > obvSignal and accDistValue > accDistSignal
    enterLong = flowAgreement and (not flowAgreement[1]) and (close > priceFilter)
    flowEnded = not flowAgreement or close < priceFilter
    riskExceeded = strategy.position_size > 0 and close < strategy.position_avg_price - atrValue * maximumAtrLoss

    if strategy.position_size == 0 and enterLong:
        strategy.entry('Conduit Long', strategy.long)
    elif strategy.position_size > 0 and (flowEnded or riskExceeded):
        strategy.close('Conduit Long', comment='ATR risk' if riskExceeded else 'Flow ended')

    plot(priceFilter, 'Price Filter', color=color.orange)
    plot(obvValue - obvSignal, 'OBV Distance', color=color.blue, display=display.data_window)
    plot(accDistValue - accDistSignal, 'AccDist Distance', color=color.green, display=display.data_window)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
