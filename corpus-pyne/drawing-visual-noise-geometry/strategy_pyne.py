"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, close, color, extend, high, label, line, linefill, na, open,
    script, size, strategy, string, ta, xloc
)
from pynecore.types import Line, LineFill, Persistent


@script.strategy("drawing-visual-noise-geometry", overlay=True, pyramiding=0, default_qty_type=strategy.fixed, default_qty_value=1, max_labels_count=50)
def main():
    sma = ta.sma(close, 14)
    lv: Persistent[Line] = na(Line)
    lv2: Persistent[Line] = na(Line)
    lf: Persistent[LineFill] = na(LineFill)
    if na(lv):
        lv = line.new(bar_index, sma, bar_index + 1, sma, color=color.green if close > open else color.red, style=line.style_dashed, width=3 if close > sma else 1, extend=extend.both, xloc=xloc.bar_index)
        lv2 = line.new(bar_index, sma, bar_index + 1, sma, color=color.blue)
        lf = linefill.new(lv, lv2, color.new(color.purple, 90))
    else:
        line.set_y1(lv, sma)
        line.set_y2(lv, sma)
        line.set_color(lv, color.new(color.blue, 50))
        line.set_width(lv, 2)
        line.set_style(lv, line.style_dotted)
    lbl = label.new(bar_index, high, text=string.tostring(sma), color=color.red, textcolor=color.white, style=label.style_label_down, size=size.small)
    label.set_text(lbl, 'x')
    level = line.get_y2(lv)
    eUp = ta.crossover(close, level)
    eDn = ta.crossunder(close, level)
    if eUp:
        strategy.entry('L', strategy.long)
    if strategy.position_size > 0 and eDn:
        strategy.close('L')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
