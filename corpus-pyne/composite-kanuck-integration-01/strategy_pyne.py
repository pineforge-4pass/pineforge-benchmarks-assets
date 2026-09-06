"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, display, input, math, na, plot, script, strategy, ta
from pynecore.types import Persistent, PersistentSeries


@script.strategy("PF probe kanuck-probe-integration", shorttitle="PF_kanINT", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False, calc_on_every_tick=True, max_bars_back=500)
def main(
    i_kama_len=input.int(14, "KAMA length", minval=2),
    i_kama_fast=input.int(2, "KAMA fast end", minval=1),
    i_kama_slow=input.int(30, "KAMA slow end", minval=2),
    i_step=input.int(2, "Tick-counter modulo", minval=1),
    i_sma_len=input.int(400, "Long SMA length", minval=50),
    i_rsi_offset=input.int(200, "RSI source offset", minval=1),
    i_deep_lag=input.int(450, "Close-reference lag", minval=1)
):

    change_n: float = math.abs(close - close[i_kama_len])
    vol_sum: float = math.sum(math.abs(close - close[1]), i_kama_len)
    er: float = change_n / vol_sum if vol_sum > 0 else 0.0
    fast_sc: float = 2.0 / (i_kama_fast + 1)
    slow_sc: float = 2.0 / (i_kama_slow + 1)
    sc: float = math.pow(er * (fast_sc - slow_sc) + slow_sc, 2)
    kama: PersistentSeries[float] = na(float)
    kama = close if na(kama[1]) else kama[1] + sc * (close - kama[1])

    tick_counter: Persistent[int] = 0
    tick_counter += 1
    gate: bool = tick_counter % i_step == 0

    long_sma: float = ta.sma(close, i_sma_len)
    deep_rsi: float = ta.rsi(close[i_rsi_offset], 14)
    deep_close: float = close[i_deep_lag]
    deep_ready: bool = not na(long_sma) and (not na(deep_rsi)) and (not na(deep_close))

    plot(long_sma, 'deep SMA', color=color.new(color.blue, 0))
    plot(deep_rsi, 'deep RSI', color=color.new(color.purple, 0), display=display.data_window)
    plot(deep_close, 'deep ref', color=color.new(color.gray, 0), display=display.data_window)

    kama_up: bool = ta.crossover(close, kama)
    kama_down: bool = ta.crossunder(close, kama)

    go_long: bool = deep_ready and kama_up and gate
    go_short: bool = deep_ready and kama_down and gate

    if go_long and strategy.position_size <= 0:
        strategy.entry('L', strategy.long, qty=1, comment='integ long')

    if go_short and strategy.position_size >= 0:
        strategy.entry('S', strategy.short, qty=1, comment='integ short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
