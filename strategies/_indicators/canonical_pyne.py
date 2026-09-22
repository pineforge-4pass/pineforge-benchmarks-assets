"""
@pyne edge

This code was compiled by PyneComp v6.0.68 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, plot, script, ta


@script.indicator("Canonical Indicators", overlay=False)
def main():
    ema21 = ta.ema(close, 21)
    sma21 = ta.sma(close, 21)
    rsi14 = ta.rsi(close, 14)
    atr14 = ta.atr(14)
    macd, signal, hist = ta.macd(close, 12, 26, 9)
    bb_basis, bb_upper, bb_lower = ta.bb(close, 20, 2.0)

    plot(ema21, 'ema21')
    plot(sma21, 'sma21')
    plot(rsi14, 'rsi14')
    plot(atr14, 'atr14')
    plot(macd, 'macd_line')
    plot(signal, 'macd_signal')
    plot(hist, 'macd_hist')
    plot(bb_basis, 'bb_basis')
    plot(bb_upper, 'bb_upper')
    plot(bb_lower, 'bb_lower')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
