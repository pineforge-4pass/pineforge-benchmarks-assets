"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_udt import udt
from pynecore.lib import array, bar_index, close, line, na, nz, script, strategy, ta
from pynecore.types import Line, Persistent


@udt
class Store:
    lines: list[Line] = na(list)


@script.strategy("drawing-udt-alias-identity", overlay=True, pyramiding=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main():
    s: Persistent[Store] = Store(array.new_line())
    alias: Persistent[Line] = na(Line)
    target = ta.sma(close, 18)
    if na(alias):
        l = line.new(bar_index, target, bar_index, target)
        array.push(s.lines, l)
        alias = l
    lvl: float = na(float)
    if array.size(s.lines) > 0:
        e = array.get(s.lines, 0)
        line.set_y2(e, target)
        lvl = line.get_y2(alias)
    ref = nz(lvl, close)
    ready = not na(lvl)
    eUp = ta.crossover(close, ref)
    eDn = ta.crossunder(close, ref)
    if ready and eUp:
        strategy.entry('L', strategy.long)
    if strategy.position_size > 0 and ready and eDn:
        strategy.close('L')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
