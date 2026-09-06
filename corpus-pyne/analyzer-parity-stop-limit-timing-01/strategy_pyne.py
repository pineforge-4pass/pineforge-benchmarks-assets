"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, hour, input, minute, na, script, strategy, ta


@script.strategy("Parity probe 01 - stop/limit timing", shorttitle="par_p01", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=0, process_orders_on_close=False)
def main(
    i_atr_len=input.int(14, "ATR Length"),
    i_stop_x=input.float(1.0, "Stop = N x ATR", minval=0.1),
    i_tp_x=input.float(2.0, "TP   = N x ATR", minval=0.1)
):

    atr_val: float = ta.atr(i_atr_len)

    at_entry_window: bool = (hour == 0 or hour == 12) and minute == 0
    fire: bool = at_entry_window and strategy.position_size == 0 and (not na(atr_val))

    if fire:
        stop_lvl: float = close - atr_val * i_stop_x
        tp_lvl: float = close + atr_val * i_tp_x
        strategy.entry('L', strategy.long, comment='periodic entry')
        strategy.exit('X', from_entry='L', stop=stop_lvl, limit=tp_lvl, comment_loss='stop fill', comment_profit='tp fill')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
