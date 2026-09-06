"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, input, script, strategy, ta, time
from pynecore.types import Persistent


@script.strategy("PF IES probe 07 - cooldown + daily cap", shorttitle="IES_p07_COOL", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_fast_ema=input.int(9, "Fast EMA", minval=2, maxval=50),
    i_slow_ema=input.int(21, "Slow EMA", minval=3, maxval=100),
    i_cooldown=input.int(15, "Cooldown bars", minval=0, maxval=200),
    i_max_trades=input.int(3, "Max trades / day", minval=1, maxval=50)
):

    bars_since_trade: Persistent[int] = 999
    bars_since_trade = bars_since_trade + 1

    daily_trades: Persistent[int] = 0
    new_day: bool = ta.change(time('D')) != 0
    if new_day:
        daily_trades = 0

    emaFast: float = ta.ema(close, i_fast_ema)
    emaSlow: float = ta.ema(close, i_slow_ema)

    raw_long_signal: bool = ta.crossover(emaFast, emaSlow) and strategy.position_size == 0
    cooldown_ok: bool = bars_since_trade >= i_cooldown
    daily_cap_ok: bool = daily_trades < i_max_trades

    if raw_long_signal and cooldown_ok and daily_cap_ok:
        strategy.entry('L', strategy.long, qty=1, comment='long w/ cooldown')
        bars_since_trade = 0
        daily_trades = daily_trades + 1

    if ta.crossunder(emaFast, emaSlow) and strategy.position_size > 0:
        strategy.close('L', comment='exit long')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
