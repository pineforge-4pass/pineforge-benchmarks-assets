"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, display, input, na, plot, script, strategy, ta


@script.strategy("PF probe kanuck-probe-03-max-bars-back-500", shorttitle="PF_kan03_MBB", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False, max_bars_back=500)
def main(
    i_sma_len=input.int(400, "Long SMA length", minval=50),
    i_rsi_offset=input.int(200, "RSI source offset", minval=1),
    i_deep_lag=input.int(450, "Close-reference lookback", minval=1)
):

    long_sma: float = ta.sma(close, i_sma_len)
    deep_rsi: float = ta.rsi(close[i_rsi_offset], 14)
    deep_close: float = close[i_deep_lag]

    plot(long_sma, 'deep SMA', color=color.new(color.blue, 0))
    plot(deep_rsi, 'deep RSI', color=color.new(color.purple, 0), display=display.data_window)

    deep_ready: bool = not na(long_sma) and (not na(deep_rsi)) and (not na(deep_close))

    long_trigger: bool = deep_ready and close > deep_close
    short_trigger: bool = deep_ready and close < deep_close

    if long_trigger and strategy.position_size <= 0:
        strategy.entry('L', strategy.long, qty=1, comment='deep-history long')

    if short_trigger and strategy.position_size >= 0:
        strategy.entry('S', strategy.short, qty=1, comment='deep-history short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
