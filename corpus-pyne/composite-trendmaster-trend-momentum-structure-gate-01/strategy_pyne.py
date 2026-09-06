"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, high, input, low, script, strategy, ta
from pynecore.types import Series


@script.strategy("PF probe trendmaster-probe-04-trend-entry-gate", shorttitle="PF_TM04_GATE", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_fast=input.int(21, "Trend EMA fast", minval=3, maxval=100),
    i_slow=input.int(55, "Trend EMA slow", minval=10, maxval=200),
    i_rsi_len=input.int(14, "RSI length", minval=2, maxval=50),
    i_rsi_lo=input.float(55, "RSI long threshold", minval=50, maxval=80),
    i_rsi_hi=input.float(45, "RSI short threshold", minval=20, maxval=50),
    i_break_len=input.int(20, "Breakout window", minval=5, maxval=200)
):

    ema_fast: float = ta.ema(close, i_fast)
    ema_slow: float = ta.ema(close, i_slow)
    trend_bull: bool = ema_fast > ema_slow
    trend_bear: bool = ema_fast < ema_slow

    r: float = ta.rsi(close, i_rsi_len)
    mom_bull: bool = r > i_rsi_lo
    mom_bear: bool = r < i_rsi_hi

    hi_now: Series[float] = ta.highest(high, i_break_len)
    lo_now: Series[float] = ta.lowest(low, i_break_len)
    break_hi: float = hi_now[1]
    break_lo: float = lo_now[1]
    struct_bull: bool = close > break_hi
    struct_bear: bool = close < break_lo

    go_long: bool = trend_bull and mom_bull and struct_bull
    go_short: bool = trend_bear and mom_bear and struct_bear

    if go_long and strategy.position_size <= 0:
        strategy.entry('L', strategy.long, qty=1, comment='gate long')

    if go_short and strategy.position_size >= 0:
        strategy.entry('S', strategy.short, qty=1, comment='gate short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
