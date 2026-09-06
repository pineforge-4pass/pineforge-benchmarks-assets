"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, input, plot, script, strategy, ta


@script.strategy("PineForge — Cashflow Cash Costs", overlay=True, initial_capital=75000, default_qty_type=strategy.cash, default_qty_value=4200, pyramiding=0, commission_type=strategy.commission.cash_per_contract, commission_value=0.35, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    fastLength=input.int(22, "Fast EMA Length", minval=2, group="Signal"),
    slowLength=input.int(63, "Slow EMA Length", minval=5, group="Signal"),
    atrLength=input.int(18, "ATR Length", minval=2, group="Risk"),
    maximumAtrLoss=input.float(2.6, "Maximum ATR Loss", minval=0.5, step=0.1, group="Risk")
):
    fastLine = ta.ema(close, fastLength)
    slowLine = ta.ema(close, slowLength)
    atrValue = ta.atr(atrLength)
    enterLong = ta.crossover(fastLine, slowLine)
    trendEnded = ta.crossunder(fastLine, slowLine)
    riskExceeded = strategy.position_size > 0 and close < strategy.position_avg_price - atrValue * maximumAtrLoss

    if strategy.position_size == 0 and enterLong:
        strategy.entry('Cashflow Long', strategy.long)
    elif strategy.position_size > 0 and (trendEnded or riskExceeded):
        strategy.close('Cashflow Long', comment='Cash risk' if riskExceeded else 'Trend ended')

    plot(fastLine, 'Fast EMA', color=color.blue)
    plot(slowLine, 'Slow EMA', color=color.orange)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
