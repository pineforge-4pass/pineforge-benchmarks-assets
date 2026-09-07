"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method
from pynecore.core.pine_udt import udt
from pynecore.lib import close, color, input, na, plot, script, strategy, ta
from pynecore.types import Persistent


@udt
class RegimeState:
    center: float = na(float)
    strength: float = na(float)
    bullish: bool = na(bool)


@script.strategy("PineForge — Sentinel UDT Method", overlay=True, initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=6, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    emaLength=input.int(36, "Center EMA", minval=3, group="Signal"),
    rsiLength=input.int(15, "Strength RSI", minval=2, group="Signal"),
    minimumStrength=input.float(54.0, "Minimum Strength", minval=50, maxval=90, group="Signal"),
    atrLength=input.int(14, "ATR Length", minval=2, group="Risk"),
    stopAtr=input.float(2.1, "Stop ATR", minval=0.5, step=0.1, group="Risk")
):
    @method
    def refresh(self: RegimeState, nextCenter: float, nextStrength: float):
        self.center = nextCenter
        self.strength = nextStrength
        self.bullish = close > nextCenter and nextStrength > 50.0
        return self

    @method
    def permitsLong(self: RegimeState, minimumStrength: float):
        return self.bullish and self.strength >= minimumStrength

    centerValue = ta.ema(close, emaLength)
    strengthValue = ta.rsi(close, rsiLength)
    atrValue = ta.atr(atrLength)
    state: Persistent[RegimeState] = RegimeState(na, 0.0, False)
    state = refresh(state, centerValue, strengthValue)

    enterSignal = ta.crossover(strengthValue, minimumStrength) and permitsLong(state, minimumStrength)
    exitSignal = ta.crossunder(strengthValue, 48.0) or close < state.center

    if enterSignal:
        strategy.entry('Sentinel Long', strategy.long)

    if strategy.position_size > 0 and exitSignal:
        strategy.close('Sentinel Long', comment='Regime changed')

    if strategy.position_size > 0:
        strategy.exit('Sentinel Guard', from_entry='Sentinel Long', stop=strategy.position_avg_price - atrValue * stopAtr)

    plot(state.center, 'State Center', color=color.green if state.bullish else color.red)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
