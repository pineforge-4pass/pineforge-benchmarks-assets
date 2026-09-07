"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method
from pynecore.core.pine_udt import udt
from pynecore.lib import close, color, display, input, math, na, plot, script, strategy, syminfo, ta


@udt
class SwitchGauge:
    fast: float = na(float)
    slow: float = na(float)
    volatility: float = na(float)


@script.strategy("PineForge — Switchboard Method Arms", overlay=True, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=2, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    mode=input.string("Balanced", "Dispatch Mode", options=("Responsive", "Balanced", "Patient"), group="Dispatch"),
    fastLength=input.int(15, "Fast EMA Length", minval=2, group="Signal"),
    slowLength=input.int(47, "Slow EMA Length", minval=5, group="Signal"),
    atrLength=input.int(18, "ATR Length", minval=2, group="Risk"),
    entryScore=input.float(0.32, "Entry Score", minval=-5, maxval=5, step=0.01, group="Signal"),
    maximumAtrLoss=input.float(2.3, "Maximum ATR Loss", minval=0.5, step=0.1, group="Risk")
):
    @method
    def weightedSpread(self: SwitchGauge, sensitivity: float):
        return (self.fast - self.slow) / math.max(self.volatility, syminfo.mintick) * sensitivity

    gauge: SwitchGauge = SwitchGauge(ta.ema(close, fastLength), ta.ema(close, slowLength), ta.atr(atrLength))
    __block_result__ = na
    __switch__ = mode
    if __switch__ == "Responsive":
        __block_result__ = weightedSpread(gauge, 1.55)
    elif __switch__ == "Balanced":
        __block_result__ = weightedSpread(gauge, 1.0)
    else:
        __block_result__ = weightedSpread(gauge, 0.68)
    score = __block_result__

    enterLong = ta.crossover(score, entryScore)
    regimeEnded = score < 0
    riskExceeded = strategy.position_size > 0 and close < strategy.position_avg_price - gauge.volatility * maximumAtrLoss

    if strategy.position_size == 0 and enterLong:
        strategy.entry('Switchboard Long', strategy.long)
    elif strategy.position_size > 0 and (regimeEnded or riskExceeded):
        strategy.close('Switchboard Long', comment='ATR risk' if riskExceeded else 'Dispatch ended')

    plot(gauge.slow, 'Slow EMA', color=color.orange)
    plot(score, 'Dispatched Score', color=color.blue, display=display.data_window)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
