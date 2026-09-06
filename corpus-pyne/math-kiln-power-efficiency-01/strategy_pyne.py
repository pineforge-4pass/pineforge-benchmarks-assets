"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, display, input, math, plot, script, strategy, syminfo, ta


@script.strategy("PineForge — Kiln Power Efficiency", overlay=True, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=2, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    trendLength=input.int(43, "Trend EMA Length", minval=5, group="Trend"),
    efficiencyLength=input.int(18, "Efficiency Window", minval=3, group="Efficiency"),
    minimumEfficiency=input.float(0.035, "Minimum Squared Efficiency", minval=0.001, maxval=1.0, step=0.001, group="Efficiency"),
    atrLength=input.int(18, "ATR Length", minval=2, group="Risk"),
    maximumAtrLoss=input.float(2.7, "Maximum ATR Loss", minval=0.5, step=0.1, group="Risk")
):
    trendLine = ta.ema(close, trendLength)
    atrValue = ta.atr(atrLength)
    displacement = math.abs(close - close[efficiencyLength])
    pathProxy = math.max(atrValue * efficiencyLength, syminfo.mintick)
    efficiency = math.pow(displacement / pathProxy, 2)

    enterLong = ta.crossover(close, trendLine) and efficiency > minimumEfficiency
    trendEnded = ta.crossunder(close, trendLine) or efficiency < minimumEfficiency * 0.35
    riskExceeded = strategy.position_size > 0 and close < strategy.position_avg_price - atrValue * maximumAtrLoss

    if strategy.position_size == 0 and enterLong:
        strategy.entry('Kiln Long', strategy.long)
    elif strategy.position_size > 0 and (trendEnded or riskExceeded):
        strategy.close('Kiln Long', comment='ATR risk' if riskExceeded else 'Efficiency ended')

    plot(trendLine, 'Trend EMA', color=color.orange)
    plot(efficiency, 'Squared Efficiency', color=color.red, display=display.data_window)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
