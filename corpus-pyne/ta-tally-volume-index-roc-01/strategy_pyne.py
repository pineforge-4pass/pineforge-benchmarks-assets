"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, display, input, plot, script, strategy, ta
from pynecore.types import Series


@script.strategy("PineForge — Tally Volume Index ROC", overlay=True, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=2, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    nviGrowthLength=input.int(83, "NVI Growth Window", minval=5, group="Volume Growth"),
    pviGrowthLength=input.int(61, "PVI Growth Window", minval=5, group="Volume Growth"),
    minimumNviGrowth=input.float(0.55, "Minimum NVI Growth %", minval=-10, maxval=10, step=0.05, group="Volume Growth"),
    minimumPviGrowth=input.float(0.35, "Minimum PVI Growth %", minval=-10, maxval=10, step=0.05, group="Volume Growth"),
    trendLength=input.int(53, "Trend EMA Length", minval=5, group="Trend"),
    atrLength=input.int(20, "ATR Length", minval=2, group="Risk"),
    maximumAtrLoss=input.float(2.6, "Maximum ATR Loss", minval=0.5, step=0.1, group="Risk")
):
    nviGrowth = ta.roc(ta.nvi, nviGrowthLength)
    pviGrowth = ta.roc(ta.pvi, pviGrowthLength)
    trendLine = ta.ema(close, trendLength)
    atrValue = ta.atr(atrLength)

    growthAgreement: Series = nviGrowth > minimumNviGrowth and pviGrowth > minimumPviGrowth
    enterLong = growthAgreement and (not growthAgreement[1]) and (close > trendLine)
    growthEnded = nviGrowth < -minimumNviGrowth * 0.5 or pviGrowth < -minimumPviGrowth * 0.5 or close < trendLine
    riskExceeded = strategy.position_size > 0 and close < strategy.position_avg_price - atrValue * maximumAtrLoss

    if strategy.position_size == 0 and enterLong:
        strategy.entry('Tally Long', strategy.long)
    elif strategy.position_size > 0 and (growthEnded or riskExceeded):
        strategy.close('Tally Long', comment='ATR risk' if riskExceeded else 'Growth ended')

    plot(trendLine, 'Trend EMA', color=color.orange)
    plot(nviGrowth, 'NVI Growth %', color=color.purple, display=display.data_window)
    plot(pviGrowth, 'PVI Growth %', color=color.blue, display=display.data_window)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
