"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_udt import udt
from pynecore.lib import close, currency, na, request, script, strategy, syminfo, ta
from pynecore.types import Persistent


@udt
class Counter:
    hits: int = 0
    last: float = 0.0


@script.strategy("PF varip-reject probe 02 - var UDT in security", shorttitle="VRIP_p02_UDT", overlay=True, initial_capital=1000000, currency=currency.USD, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    c: Persistent[Counter] = Counter(0, 0.0)
    def htfCross():
        fastH = ta.ema(close, 9)
        slowH = ta.ema(close, 21)
        return 1 if ta.crossover(fastH, slowH) else 0

    htfFiredInt: int = request.security(syminfo.tickerid, '60', htfCross())
    htfFired: bool = htfFiredInt == 1

    if htfFired:
        c.hits = c.hits + 1
        c.last = close

    rsiVal = ta.rsi(close, 14)

    entryCond: bool = c.hits > 0 and htfFired and (not na(rsiVal)) and (rsiVal > 50.0)
    exitCond: bool = not na(rsiVal) and rsiVal < 40.0

    if entryCond and strategy.position_size == 0:
        strategy.entry('L', strategy.long, qty=1, comment='entry long')
    if exitCond and strategy.position_size > 0:
        strategy.close('L', comment='exit long')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
