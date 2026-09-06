"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, barmerge, close, high, hour, input, minute, request, script,
    strategy, syminfo, ta
)
from pynecore.types import Series


@script.strategy("PF Analyzer (PineForge)", shorttitle="PF_analyze", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    mode=input.string("clock_pulse", "Analysis mode", options=("clock_pulse", "htf_60_roll", "htf_d_high1", "bar_stair")),
    stepBars=input.int(96, "clock_pulse: unused (legacy bar step)", minval=2)
):

    inPulse = bar_index > 0 and hour == 0 and (minute == 15)
    exitPulse = bar_index > 0 and hour == 0 and (minute == 30)

    h60 = request.security(syminfo.tickerid, '60', close, lookahead=barmerge.lookahead_off)
    roll60: Series = ta.change(h60) != 0

    dH1: Series = request.security(syminfo.tickerid, 'D', high[1], lookahead=barmerge.lookahead_off)
    crossUp = close > dH1 and close[1] <= dH1[1]
    exitD = close < dH1 * 0.995 and strategy.position_size > 0

    stair = close > close[1] and close[1] > close[2]

    if mode == 'clock_pulse':
        if exitPulse:
            strategy.close('C')
        if inPulse:
            strategy.entry('C', strategy.long, qty=1)

    if mode == 'htf_60_roll':
        if roll60 and strategy.position_size == 0:
            strategy.entry('R', strategy.long, qty=1)
        if roll60[1] and strategy.position_size != 0:
            strategy.close('R')

    if mode == 'htf_d_high1':
        if crossUp and strategy.position_size == 0:
            strategy.entry('L', strategy.long, qty=1)
        if exitD:
            strategy.close('L')

    if mode == 'bar_stair':
        if stair and strategy.position_size == 0:
            strategy.entry('S', strategy.long, qty=1)
        if not stair and strategy.position_size > 0:
            strategy.close('S')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
