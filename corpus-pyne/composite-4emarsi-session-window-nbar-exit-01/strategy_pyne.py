"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, input, na, script, strategy, ta, time, timeframe
from pynecore.types import Persistent


@script.strategy("PF probe 4ema-rsi-probe-03-binary-bar-window", shorttitle="PF_4ema03_WIN", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_expiry_bars=input.int(8, "Forced exit after N bars", minval=1),
    i_session=input.session("1000-2200", "Entry session (UTC)")
):

    in_window: bool = not na(time(timeframe.period, i_session, 'UTC'))

    fast: float = ta.ema(close, 5)
    slow: float = ta.ema(close, 20)
    long_trigger: bool = ta.crossover(fast, slow) and in_window
    short_trigger: bool = ta.crossunder(fast, slow) and in_window

    bars_in_trade: Persistent[int] = 0
    if strategy.position_size != 0:
        bars_in_trade += 1
    else:
        bars_in_trade = 0

    expiry_due: bool = strategy.position_size != 0 and bars_in_trade >= i_expiry_bars

    if long_trigger and strategy.position_size == 0:
        strategy.entry('L', strategy.long, qty=1, comment='window long')

    if short_trigger and strategy.position_size == 0:
        strategy.entry('S', strategy.short, qty=1, comment='window short')

    if expiry_due:
        strategy.close_all(comment='bar-window expiry')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
