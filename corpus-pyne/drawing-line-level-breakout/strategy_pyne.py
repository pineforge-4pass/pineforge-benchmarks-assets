"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import bar_index, close, color, extend, line, na, script, strategy, ta
from pynecore.types import Line, Persistent


@script.strategy("drawing-line-level-breakout", overlay=True, pyramiding=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main():
    levelSrc = ta.sma(close, 20)
    res: Persistent[Line] = na(Line)
    level: float = na(float)
    if not na(levelSrc):
        if na(res):
            res = line.new(bar_index - 1, levelSrc, bar_index, levelSrc, color=color.red, width=2, extend=extend.right)
        else:
            cur = line.get_y2(res)
            line.set_xy2(res, bar_index, cur + (levelSrc - cur) * 0.35)
        level = line.get_y2(res)
    ready = not na(level)
    eUp = ready and ta.crossover(close, level)
    eDn = ready and ta.crossunder(close, level)
    if ready and eUp:
        strategy.entry('L', strategy.long)
    if strategy.position_size > 0 and ready and eDn:
        strategy.close('L')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
