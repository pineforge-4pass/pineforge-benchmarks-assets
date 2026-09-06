"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import barmerge, close, request, script, strategy, syminfo, ta


@script.strategy("PF MTF probe - weekly SMA(10) cross", shorttitle="MTF_WSMA", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    wsma: float = request.security(syminfo.tickerid, 'W', ta.sma(close, 10), lookahead=barmerge.lookahead_off)
    if ta.crossover(close, wsma):
        strategy.entry('L', strategy.long, comment='close x up weekly SMA')
    if ta.crossunder(close, wsma):
        strategy.entry('S', strategy.short, comment='close x dn weekly SMA')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
