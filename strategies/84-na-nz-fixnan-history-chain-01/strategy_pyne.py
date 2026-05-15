"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, currency, fixnan, na, nz, script, strategy, ta
from pynecore.types import Series


@script.strategy("PF TV golden 49 - na nz history", shorttitle="PF_G49_NA", overlay=True, initial_capital=1000000, currency=currency.USD, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    rawDelta = close - close[1]
    safeDelta = nz(rawDelta, 0)
    heldDelta = fixnan(rawDelta)
    score: Series = ta.sma(safeDelta + nz(heldDelta, 0), 8)

    longSignal = not na(score) and score > 0 and (nz(score[1], 0) <= 0)
    flatSignal = not na(score) and score < 0 and (nz(score[1], 0) >= 0)

    if longSignal and strategy.position_size == 0:
        strategy.entry('N', strategy.long, qty=1, comment='na chain long')

    if flatSignal and strategy.position_size > 0:
        strategy.close('N', comment='na chain flat')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
