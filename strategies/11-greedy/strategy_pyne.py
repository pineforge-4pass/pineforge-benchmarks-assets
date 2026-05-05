"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, currency, high, input, low, na, open, script, strategy, syminfo


@script.strategy("Greedy Strategy", calc_on_order_fills=False, overlay=True, use_bar_magnifier=False, initial_capital=1000000, currency=currency.USD, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    tp=input(10, "Take profit"),
    sl=input(10, "Stop loss"),
    maxidf=input(title="Max intraday filled orders", defval=5)
):
    strategy.risk.max_intraday_filled_orders(maxidf)
    upGap = open > high[1]
    dnGap = open < low[1]
    dn = strategy.position_size < 0 and open > close
    up = strategy.position_size > 0 and open < close
    if upGap:
        strategy.entry('GapUp', strategy.long, stop=high[1])
    else:
        strategy.cancel('GapUp')
    if dn:
        strategy.entry('Dn', strategy.short, stop=close)
    else:
        strategy.cancel('Dn')
    if dnGap:
        strategy.entry('GapDn', strategy.short, stop=low[1])
    else:
        strategy.cancel('GapDn')
    if up:
        strategy.entry('Up', strategy.long, stop=close)
    else:
        strategy.cancel('Up')
    XQty = -strategy.position_size if strategy.position_size < 0 else strategy.position_size
    dir = -1 if strategy.position_size < 0 else 1
    lmP = strategy.position_avg_price + dir * tp * syminfo.mintick
    slP = strategy.position_avg_price - dir * sl * syminfo.mintick
    nav: float = na(float)
    revCond = dnGap if strategy.position_size > 0 else upGap if strategy.position_size < 0 else False
    if not revCond and XQty > 0:
        strategy.order('TP', strategy.long if strategy.position_size < 0 else strategy.short, XQty, lmP, nav, 'TPSL', strategy.oca.reduce, 'TPSL')
        strategy.order('SL', strategy.long if strategy.position_size < 0 else strategy.short, XQty, nav, slP, 'TPSL', strategy.oca.reduce, 'TPSL')
    if XQty == 0 or revCond:
        strategy.cancel('TP')
        strategy.cancel('SL')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)