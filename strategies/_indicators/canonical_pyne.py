"""@pyne
PyneCore counterpart of canonical.pine — computes the same set of
TA indicators on the reference OHLCV, returns per-bar values via plot()
which PyneCore writes to its output CSV.
"""
from pynecore.lib import script, ta, close, plot


@script.indicator("Canonical Indicators")
def main():
    ema21 = ta.ema(close, 21)
    sma21 = ta.sma(close, 21)
    rsi14 = ta.rsi(close, 14)
    atr14 = ta.atr(14)
    macd_line, macd_signal, macd_hist = ta.macd(close, 12, 26, 9)
    bb_basis, bb_upper, bb_lower = ta.bb(close, 20, 2.0)

    plot(ema21,       "ema21")
    plot(sma21,       "sma21")
    plot(rsi14,       "rsi14")
    plot(atr14,       "atr14")
    plot(macd_line,   "macd_line")
    plot(macd_signal, "macd_signal")
    plot(macd_hist,   "macd_hist")
    plot(bb_basis,    "bb_basis")
    plot(bb_upper,    "bb_upper")
    plot(bb_lower,    "bb_lower")
