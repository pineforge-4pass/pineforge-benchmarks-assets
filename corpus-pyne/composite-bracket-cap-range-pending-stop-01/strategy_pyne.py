"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, high, input, low, math, na, open, script, strategy, syminfo, ta
from pynecore.types import Series


@script.strategy("PF probe 97 - tp/sl gap reversal oca", shorttitle="PF_p97_TPSL_OCA", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    i_tp_ticks=input.int(10, "Take profit (ticks)", minval=1),
    i_sl_ticks=input.int(10, "Stop loss (ticks)", minval=1),
    i_max_fills=input.int(5, "Max intraday filled orders", minval=1),
    i_atr_len=input.int(14, "ATR length", minval=1),
    i_atr_mult=input.float(1.0, "Range/ATR threshold", minval=0.1)
):
    strategy.risk.max_intraday_filled_orders(i_max_fills)

    prev_range: float = high[1] - low[1]
    atr_now: Series[float] = ta.atr(i_atr_len)
    atr_prev: float = atr_now[1]
    expansion: bool = not na(atr_prev) and prev_range > atr_prev * i_atr_mult

    prev_up: bool = close[1] > open[1]
    prev_down: bool = close[1] < open[1]

    arm_long: bool = expansion and prev_up
    arm_short: bool = expansion and prev_down

    if arm_long:
        strategy.entry('LongOnGap', strategy.long, stop=high[1])
    else:
        strategy.cancel('LongOnGap')

    if arm_short:
        strategy.entry('ShortOnGap', strategy.short, stop=low[1])
    else:
        strategy.cancel('ShortOnGap')

    pos_qty: float = math.abs(strategy.position_size)
    pos_dir: int = 1 if strategy.position_size > 0 else -1 if strategy.position_size < 0 else 0
    entry_px: float = strategy.position_avg_price
    tp_px: float = entry_px + pos_dir * i_tp_ticks * syminfo.mintick
    sl_px: float = entry_px - pos_dir * i_sl_ticks * syminfo.mintick

    in_position: bool = pos_qty > 0
    exit_dir = strategy.short if pos_dir > 0 else strategy.long

    if in_position:
        strategy.order('BracketTP', exit_dir, qty=pos_qty, limit=tp_px, oca_name='bracket97', oca_type=strategy.oca.reduce, comment='TP')

        strategy.order('BracketSL', exit_dir, qty=pos_qty, stop=sl_px, oca_name='bracket97', oca_type=strategy.oca.reduce, comment='SL')
    else:
        strategy.cancel('BracketTP')
        strategy.cancel('BracketSL')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
