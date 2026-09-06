"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import bar_index, close, line, na, script, strategy, ta
from pynecore.types import Line, Persistent


@script.strategy("drawing-delete-halt", overlay=True, pyramiding=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main():
    sma = ta.sma(close, 20)
    lv: Persistent[Line] = na(Line)
    entries: Persistent[int] = 0
    if na(lv):
        lv = line.new(bar_index, sma, bar_index, sma)
    else:
        line.set_y2(lv, sma)
    level = line.get_y2(lv)
    eUp = ta.crossover(close, level)
    eDn = ta.crossunder(close, level)
    if eUp:
        strategy.entry('L', strategy.long)
        entries += 1
    if strategy.position_size > 0 and eDn:
        strategy.close('L')
    if entries == 5:
        line.delete(lv)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
