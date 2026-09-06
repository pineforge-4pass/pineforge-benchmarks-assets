"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, input, script, strategy, syminfo, ta


@script.strategy("PF probe scalping-probe-01-tight-tp-sl-points", shorttitle="PF_SC01_BRK", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_fast=input.int(5, "Fast EMA", minval=2, maxval=50),
    i_slow=input.int(13, "Slow EMA", minval=3, maxval=100),
    i_tp_tk=input.int(15, "Take profit (ticks)", minval=1),
    i_sl_tk=input.int(7, "Stop loss (ticks)", minval=1)
):

    ema_fast: float = ta.ema(close, i_fast)
    ema_slow: float = ta.ema(close, i_slow)

    long_signal: bool = ta.crossover(ema_fast, ema_slow)
    short_signal: bool = ta.crossunder(ema_fast, ema_slow)

    if long_signal:
        strategy.entry('L', strategy.long, qty=1, comment='scalp long')

    if short_signal:
        strategy.entry('S', strategy.short, qty=1, comment='scalp short')

    entry_px: float = strategy.position_avg_price

    if strategy.position_size > 0:
        tp_px: float = entry_px + i_tp_tk * syminfo.mintick
        sl_px: float = entry_px - i_sl_tk * syminfo.mintick
        strategy.exit('Brk', from_entry='L', stop=sl_px, limit=tp_px)

    if strategy.position_size < 0:
        tp_px: float = entry_px - i_tp_tk * syminfo.mintick
        sl_px: float = entry_px + i_sl_tk * syminfo.mintick
        strategy.exit('Brk', from_entry='S', stop=sl_px, limit=tp_px)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
