"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import bar_index, close, color, high, input, line, low, na, script, strategy, ta
from pynecore.types import Persistent, Series


@script.strategy("PF probe trendmaster-probe-integration", shorttitle="PF_TMINT", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False, max_lines_count=500)
def main(
    i_pivot=input.int(5, "Pivot strength", minval=2, maxval=20),
    i_ema_fast=input.int(21, "EMA fast", minval=3, maxval=100),
    i_ema_mid=input.int(55, "EMA mid", minval=10, maxval=200),
    i_ema_slow=input.int(200, "EMA slow", minval=50, maxval=500),
    i_rsi_len=input.int(14, "RSI length", minval=2, maxval=50),
    i_rsi_lo=input.float(55, "RSI long threshold", minval=50, maxval=80),
    i_rsi_hi=input.float(45, "RSI short threshold", minval=20, maxval=50),
    i_break_len=input.int(20, "Breakout window", minval=5, maxval=200),
    i_rr=input.float(2.0, "Reward:risk ratio", minval=0.5, maxval=10.0, step=0.5)
):

    ph: float = ta.pivothigh(high, i_pivot, i_pivot)
    pl: float = ta.pivotlow(low, i_pivot, i_pivot)

    last_ph: Persistent[float] = na(float)
    last_pl: Persistent[float] = na(float)
    last_ph_x: Persistent[int] = na(int)
    last_pl_x: Persistent[int] = na(int)
    prev_ph_y: Persistent[float] = na(float)
    prev_ph_x: Persistent[int] = na(int)
    prev_pl_y: Persistent[float] = na(float)
    prev_pl_x: Persistent[int] = na(int)

    if not na(ph):
        cur_x: int = bar_index - i_pivot
        if not na(last_ph) and (not na(last_ph_x)):
            line.new(last_ph_x, last_ph, cur_x, ph, color=color.red)
        prev_ph_y = last_ph
        prev_ph_x = last_ph_x
        last_ph = ph
        last_ph_x = cur_x

    if not na(pl):
        cur_x: int = bar_index - i_pivot
        if not na(last_pl) and (not na(last_pl_x)):
            line.new(last_pl_x, last_pl, cur_x, pl, color=color.green)
        prev_pl_y = last_pl
        prev_pl_x = last_pl_x
        last_pl = pl
        last_pl_x = cur_x

    ema_fast: float = ta.ema(close, i_ema_fast)
    ema_mid: float = ta.ema(close, i_ema_mid)
    ema_slow: float = ta.ema(close, i_ema_slow)

    stack_bull: bool = ema_fast > ema_mid and ema_mid > ema_slow
    stack_bear: bool = ema_fast < ema_mid and ema_mid < ema_slow

    trend_bull: bool = ema_fast > ema_mid
    trend_bear: bool = ema_fast < ema_mid

    r: float = ta.rsi(close, i_rsi_len)
    mom_bull: bool = r > i_rsi_lo
    mom_bear: bool = r < i_rsi_hi

    hi_now: Series[float] = ta.highest(high, i_break_len)
    lo_now: Series[float] = ta.lowest(low, i_break_len)
    break_hi: float = hi_now[1]
    break_lo: float = lo_now[1]
    struct_bull: bool = close > break_hi
    struct_bear: bool = close < break_lo

    gate_long: bool = trend_bull and mom_bull and struct_bull
    gate_short: bool = trend_bear and mom_bear and struct_bear

    go_long: bool = stack_bull and gate_long and (not na(last_pl))
    go_short: bool = stack_bear and gate_short and (not na(last_ph))

    if go_long and strategy.position_size <= 0:
        strategy.entry('L', strategy.long, qty=1, comment='integ trend long')

    if go_short and strategy.position_size >= 0:
        strategy.entry('S', strategy.short, qty=1, comment='integ trend short')

    entry_px: float = strategy.position_avg_price

    if strategy.position_size > 0 and (not na(last_pl)):
        sl_px: float = last_pl
        tp_px: float = entry_px + (entry_px - last_pl) * i_rr
        strategy.exit('Brk', from_entry='L', stop=sl_px, limit=tp_px)

    if strategy.position_size < 0 and (not na(last_ph)):
        sl_px: float = last_ph
        tp_px: float = entry_px - (last_ph - entry_px) * i_rr
        strategy.exit('Brk', from_entry='S', stop=sl_px, limit=tp_px)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
