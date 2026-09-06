"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method_call
from pynecore.lib import array, bar_index, box, close, color, high, low, script, strategy
from pynecore.types import Box, Persistent


@script.strategy("drawing-box-zone-reentry", overlay=True, pyramiding=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main():
    zones: Persistent[list[Box]] = array.new_box()
    gapUp = low > high[2]
    if gapUp:
        array.push(zones, box.new(bar_index - 2, low, bar_index, high[2], bgcolor=color.new(color.green, 80)))
    n = array.size(zones)
    if n > 0:
        z = array.get(zones, n - 1)
        top = box.get_top(z)
        bot = box.get_bottom(z)
        if strategy.position_size == 0 and close <= top and (close >= bot):
            strategy.entry('L', strategy.long)
        if strategy.position_size > 0 and close > top:
            strategy.close('L')
            method_call('delete', array.get(zones, n - 1))
            array.pop(zones)
    if array.size(zones) > 20:
        method_call('delete', array.get(zones, 0))
        array.shift(zones)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
