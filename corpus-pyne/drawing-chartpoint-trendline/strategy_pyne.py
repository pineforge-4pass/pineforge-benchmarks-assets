"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import bar_index, chart, close, line, na, nz, script, strategy, ta
from pynecore.types import Line, Persistent, Series


@script.strategy("drawing-chartpoint-trendline", overlay=True, pyramiding=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main():
    trend: Persistent[Line] = na(Line)
    base: Series = ta.sma(close, 20)
    proj: float = na(float)
    if not na(base) and (not na(base[2])):
        p1 = chart.point.from_index(bar_index - 2, base[2])
        p2 = chart.point.from_index(bar_index, base)
        if na(trend):
            trend = line.new(p1, p2)
        else:
            line.set_first_point(trend, p1)
            line.set_second_point(trend, p2)
        proj = line.get_price(trend, bar_index - 1)
    ref = nz(proj, close)
    ready = not na(proj)
    sDn = ta.crossunder(close, ref)
    sUp = ta.crossover(close, ref)
    if ready and sDn:
        strategy.entry('S', strategy.short)
    if strategy.position_size < 0 and ready and sUp:
        strategy.close('S')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
