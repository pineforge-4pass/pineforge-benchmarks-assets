"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, input, plot, script, strategy, string, ta


@script.strategy("PineForge — Glyph String Regex", overlay=True, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=2, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    configuration=input.string("Trend:Confirmed|Risk:Guarded", "Configuration Label", group="Configuration"),
    fastLength=input.int(18, "Fast EMA Length", minval=2, group="Trend"),
    slowLength=input.int(54, "Slow EMA Length", minval=5, group="Trend"),
    atrLength=input.int(16, "ATR Length", minval=2, group="Risk"),
    maximumAtrLoss=input.float(2.2, "Maximum ATR Loss", minval=0.5, step=0.1, group="Risk")
):
    normalized = string.lower(configuration)
    trendRulePresent = string.match(normalized, 'trend:[a-z]+') != ''
    confirmationRequested = string.match(normalized, 'trend:confirmed') != ''
    guardedRisk = string.match(normalized, 'risk:guarded') != ''

    fastLine = ta.ema(close, fastLength)
    slowLine = ta.ema(close, slowLength)
    rsiValue = ta.rsi(close, 14)
    atrValue = ta.atr(atrLength)
    confirmationLevel = 57.0 if confirmationRequested else 51.0
    effectiveRisk = maximumAtrLoss if guardedRisk else maximumAtrLoss * 1.4

    enterLong = trendRulePresent and ta.crossover(fastLine, slowLine) and (rsiValue > confirmationLevel)
    regimeEnded = ta.crossunder(fastLine, slowLine) or rsiValue < 44
    riskExceeded = strategy.position_size > 0 and close < strategy.position_avg_price - atrValue * effectiveRisk

    if strategy.position_size == 0 and enterLong:
        strategy.entry('Glyph Long', strategy.long)
    elif strategy.position_size > 0 and (regimeEnded or riskExceeded):
        strategy.close('Glyph Long', comment='Regex risk' if riskExceeded else 'Regex regime')

    plot(fastLine, 'Fast EMA', color=color.blue)
    plot(slowLine, 'Slow EMA', color=color.orange)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
