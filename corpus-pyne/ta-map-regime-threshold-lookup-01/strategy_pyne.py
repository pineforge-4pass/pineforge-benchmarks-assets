"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import barstate, close, map, script, strategy, ta
from pynecore.types import Persistent


@script.strategy("Map Regime Tracker", overlay=True, initial_capital=1000000, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main():
    myMap: Persistent[dict[str, float]] = map.new()
    if barstate.isfirst:
        map.put(myMap, 'bullish_limit', 1.5)
        map.put(myMap, 'bearish_limit', -1.5)

    trend = ta.ema(close, 20) > ta.sma(close, 50)
    regime_str = 'bullish' if trend else 'bearish'
    currentKey = regime_str + '_limit'

    limit = map.get(myMap, currentKey) if map.contains(myMap, currentKey) else 0.0
    mom = ta.mom(close, 10)

    if trend and mom > limit:
        strategy.entry('Long', strategy.long)
    if not trend and mom < limit:
        strategy.entry('Short', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
