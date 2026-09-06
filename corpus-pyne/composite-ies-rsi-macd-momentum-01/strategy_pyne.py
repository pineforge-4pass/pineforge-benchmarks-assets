"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, input, script, strategy, ta
from pynecore.types import Series


@script.strategy("PF IES probe 03 - rsi+macd momentum", shorttitle="IES_p03_MOM", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_rsi_len=input.int(14, "RSI Period", minval=5, maxval=30),
    i_rsi_bull=input.float(55, "RSI Bullish Level", minval=50, maxval=70),
    i_rsi_bear=input.float(45, "RSI Bearish Level", minval=30, maxval=50),
    i_macd_fast=input.int(12, "MACD Fast", minval=5, maxval=20),
    i_macd_slow=input.int(26, "MACD Slow", minval=15, maxval=50),
    i_macd_sig=input.int(9, "MACD Signal", minval=3, maxval=15)
):

    rsi: Series[float] = ta.rsi(close, i_rsi_len)
    rsi_bullish: bool = rsi > i_rsi_bull
    rsi_bearish: bool = rsi < i_rsi_bear
    rsi_momentum_up: bool = rsi > rsi[3]
    rsi_momentum_dn: bool = rsi < rsi[3]

    macd_line: float = ta.ema(close, i_macd_fast) - ta.ema(close, i_macd_slow)
    macd_signal: float = ta.ema(macd_line, i_macd_sig)
    macd_hist: Series[float] = macd_line - macd_signal

    macd_bullish: bool = macd_hist > 0 and macd_hist > macd_hist[1]
    macd_bearish: bool = macd_hist < 0 and macd_hist < macd_hist[1]

    momentum_bull_score: Series[int] = 0
    if rsi_bullish:
        momentum_bull_score += 1
    if rsi_momentum_up:
        momentum_bull_score += 1
    if macd_bullish:
        momentum_bull_score += 1

    momentum_bear_score: Series[int] = 0
    if rsi_bearish:
        momentum_bear_score += 1
    if rsi_momentum_dn:
        momentum_bear_score += 1
    if macd_bearish:
        momentum_bear_score += 1

    long_entry: bool = momentum_bull_score >= 2 and momentum_bull_score[1] < 2 and (strategy.position_size <= 0)
    short_entry: bool = momentum_bear_score >= 2 and momentum_bear_score[1] < 2 and (strategy.position_size >= 0)

    if long_entry:
        if strategy.position_size < 0:
            strategy.close('S', comment='flip')
        strategy.entry('L', strategy.long, qty=1, comment='mom 2of3 long')

    if short_entry:
        if strategy.position_size > 0:
            strategy.close('L', comment='flip')
        strategy.entry('S', strategy.short, qty=1, comment='mom 2of3 short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
