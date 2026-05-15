"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, currency, input, math, script, strategy, syminfo, ta


@script.strategy("PF probe 97a - tp/sl bracket isolate", shorttitle="PF_p97a_BRK", overlay=True, initial_capital=1000000, currency=currency.USD, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    i_fast=input.int(9, "Fast MA", minval=2),
    i_slow=input.int(21, "Slow MA", minval=3),
    i_tp_ticks=input.int(10, "Take profit (ticks)", minval=1),
    i_sl_ticks=input.int(10, "Stop loss (ticks)", minval=1)
):

    fast: float = ta.sma(close, i_fast)
    slow: float = ta.sma(close, i_slow)
    go_long: bool = ta.crossover(fast, slow)
    go_short: bool = ta.crossunder(fast, slow)

    if go_long and strategy.position_size <= 0:
        strategy.entry('L', strategy.long, comment='ma cross up')

    if go_short and strategy.position_size >= 0:
        strategy.entry('S', strategy.short, comment='ma cross dn')

    pos_qty: float = math.abs(strategy.position_size)
    pos_dir: int = 1 if strategy.position_size > 0 else -1 if strategy.position_size < 0 else 0
    entry_px: float = strategy.position_avg_price
    tp_px: float = entry_px + pos_dir * i_tp_ticks * syminfo.mintick
    sl_px: float = entry_px - pos_dir * i_sl_ticks * syminfo.mintick

    in_position: bool = pos_qty > 0
    exit_dir = strategy.short if pos_dir > 0 else strategy.long

    if in_position:
        strategy.order('BracketTP', exit_dir, qty=pos_qty, limit=tp_px, oca_name='bracket97a', oca_type=strategy.oca.reduce, comment='TP')

        strategy.order('BracketSL', exit_dir, qty=pos_qty, stop=sl_px, oca_name='bracket97a', oca_type=strategy.oca.reduce, comment='SL')
    else:
        strategy.cancel('BracketTP')
        strategy.cancel('BracketSL')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
