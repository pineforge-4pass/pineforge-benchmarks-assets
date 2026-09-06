"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from enum import StrEnum as Enum
from pynecore.lib import close, color, input, plot, script, strategy, ta


class RelayMode(Enum):
    Trend = 'Trend'
    Reversion = 'Reversion'


@script.strategy("PineForge — Relay Enum Regime", overlay=True, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=2, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    mode=input.enum(RelayMode.Trend, "Signal Regime", group="Signal"),
    fastLength=input.int(16, "Fast EMA", minval=2, group="Signal"),
    slowLength=input.int(45, "Slow EMA", minval=3, group="Signal"),
    rsiLength=input.int(12, "RSI Length", minval=2, group="Signal"),
    reversionEntry=input.float(31.0, "Reversion Entry RSI", minval=10, maxval=45, step=0.5, group="Signal"),
    reversionExit=input.float(53.0, "Reversion Exit RSI", minval=45, maxval=75, step=0.5, group="Signal"),
    atrLength=input.int(16, "ATR Length", minval=2, group="Risk"),
    stopAtr=input.float(2.0, "Stop ATR", minval=0.5, step=0.1, group="Risk")
):
    fastEma = ta.ema(close, fastLength)
    slowEma = ta.ema(close, slowLength)
    momentum = ta.rsi(close, rsiLength)
    atrValue = ta.atr(atrLength)

    trendMode = mode == RelayMode.Trend
    entrySignal = ta.crossover(fastEma, slowEma) if trendMode else ta.crossunder(momentum, reversionEntry)
    exitSignal = ta.crossunder(fastEma, slowEma) if trendMode else ta.crossover(momentum, reversionExit)

    if entrySignal:
        strategy.entry('Relay Long', strategy.long)

    if strategy.position_size > 0 and exitSignal:
        strategy.close('Relay Long', comment='Trend relay ended' if trendMode else 'Reversion completed')

    if strategy.position_size > 0:
        strategy.exit('Relay Guard', from_entry='Relay Long', stop=strategy.position_avg_price - atrValue * stopAtr)

    plot(fastEma, 'Fast EMA', color=color.aqua)
    plot(slowEma, 'Slow EMA', color=color.blue)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
