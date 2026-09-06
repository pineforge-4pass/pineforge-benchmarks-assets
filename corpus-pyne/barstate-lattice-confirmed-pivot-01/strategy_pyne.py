"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import bar_index, barstate, close, color, input, na, plot, script, strategy, ta
from pynecore.types import Persistent


@script.strategy("PineForge — Lattice Confirmed Pivot", overlay=True, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=2, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    fastLength=input.int(17, "Fast EMA", minval=2, group="Signal"),
    slowLength=input.int(53, "Slow EMA", minval=3, group="Signal"),
    momentumLength=input.int(13, "RSI Length", minval=2, group="Signal"),
    entryMomentum=input.float(54.0, "Entry RSI", minval=40, maxval=75, step=0.5, group="Signal"),
    exitMomentum=input.float(44.0, "Exit RSI", minval=20, maxval=60, step=0.5, group="Signal"),
    confirmedOnly=input.bool(True, "Require Confirmed Bars", group="Execution"),
    maximumHoldBars=input.int(192, "Maximum Hold Bars", minval=8, group="Risk"),
    atrLength=input.int(15, "ATR Length", minval=2, group="Risk"),
    stopAtr=input.float(2.3, "Stop ATR", minval=0.5, step=0.1, group="Risk")
):
    fastEma = ta.ema(close, fastLength)
    slowEma = ta.ema(close, slowLength)
    momentum = ta.rsi(close, momentumLength)
    atrValue = ta.atr(atrLength)
    signalBarReady = not confirmedOnly or barstate.isconfirmed

    openedAt: Persistent[int] = na(int)
    if strategy.position_size > 0 and strategy.position_size[1] == 0:
        openedAt = bar_index

    entrySignal = signalBarReady and ta.crossover(fastEma, slowEma) and (momentum > entryMomentum)
    exitSignal = signalBarReady and (ta.crossunder(fastEma, slowEma) or momentum < exitMomentum)
    holdExpired = strategy.position_size > 0 and (not na(openedAt)) and (bar_index - openedAt >= maximumHoldBars)

    if entrySignal:
        strategy.entry('Lattice Long', strategy.long)

    if strategy.position_size > 0 and (exitSignal or holdExpired):
        strategy.close('Lattice Long', comment='Maximum hold' if holdExpired else 'Confirmed pivot')

    if strategy.position_size > 0:
        strategy.exit('Lattice Guard', from_entry='Lattice Long', stop=strategy.position_avg_price - atrValue * stopAtr)

    if strategy.position_size == 0:
        openedAt = na

    plot(fastEma, 'Fast EMA', color=color.teal)
    plot(slowEma, 'Slow EMA', color=color.navy)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
