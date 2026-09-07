"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, script, strategy, ta, timeframe


@script.strategy("VWAP Bands Mean Reversion 2σ", overlay=True, default_qty_type=strategy.fixed, default_qty_value=1, initial_capital=100000)
def main():
    vw, upper_band, lower_band = ta.vwap(close, timeframe.change('1D'), 2.0)
    long_condition = ta.crossunder(close, lower_band)
    exit_condition = ta.crossover(close, vw)

    if long_condition:
        strategy.entry('long', strategy.long)
    if exit_condition:
        strategy.close('long')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
