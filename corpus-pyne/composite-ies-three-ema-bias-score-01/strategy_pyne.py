"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, input, script, strategy, ta
from pynecore.types import Series


@script.strategy("PF IES probe 02 - three-ema bias", shorttitle="IES_p02_BIAS", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_ma_fast=input.int(21, "Fast MA", minval=5, maxval=50),
    i_ma_slow=input.int(55, "Slow MA", minval=20, maxval=200),
    i_ma_trend=input.int(200, "Trend MA", minval=50, maxval=500),
    i_bias_thresh=input.float(30, "Bias Threshold", minval=10, maxval=60)
):

    ma_fast: float = ta.ema(close, i_ma_fast)
    ma_slow: float = ta.ema(close, i_ma_slow)
    ma_trend: float = ta.ema(close, i_ma_trend)

    ma_bullish: bool = ma_fast > ma_slow and ma_slow > ma_trend
    ma_bearish: bool = ma_fast < ma_slow and ma_slow < ma_trend
    price_above_structure: bool = close > ma_fast and close > ma_slow
    price_below_structure: bool = close < ma_fast and close < ma_slow

    bias_score: float = 0.0
    if ma_bullish:
        bias_score += 30
    if price_above_structure:
        bias_score += 20
    if close > ma_trend:
        bias_score += 20

    bear_bias_score: float = 0.0
    if ma_bearish:
        bear_bias_score += 30
    if price_below_structure:
        bear_bias_score += 20
    if close < ma_trend:
        bear_bias_score += 20

    bullish_bias: Series[bool] = bias_score >= i_bias_thresh
    bearish_bias: Series[bool] = bear_bias_score >= i_bias_thresh

    long_entry: bool = bullish_bias and (not bullish_bias[1]) and (strategy.position_size <= 0)
    short_entry: bool = bearish_bias and (not bearish_bias[1]) and (strategy.position_size >= 0)

    if long_entry:
        if strategy.position_size < 0:
            strategy.close('S', comment='flip')
        strategy.entry('L', strategy.long, qty=1, comment='bias rising long')

    if short_entry:
        if strategy.position_size > 0:
            strategy.close('L', comment='flip')
        strategy.entry('S', strategy.short, qty=1, comment='bias rising short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
