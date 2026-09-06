"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import barstate, close, color, input, map, plot, script, strategy, ta
from pynecore.types import Persistent


@script.strategy("PineForge — Mosaic Map Regime", overlay=True, initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=5, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    centerLength=input.int(33, "Center EMA", minval=3, group="Signal"),
    atrLength=input.int(18, "ATR Length", minval=2, group="Signal"),
    expansionPct=input.float(1.8, "Expansion ATR %", minval=0.2, step=0.1, group="Signal"),
    stopAtr=input.float(2.6, "Base Stop ATR", minval=0.5, step=0.1, group="Risk")
):
    regimeWeight: Persistent[dict[str, float]] = map.new()
    if barstate.isfirst:
        map.put(regimeWeight, 'calm', 0.85)
        map.put(regimeWeight, 'active', 1.15)

    center = ta.ema(close, centerLength)
    atrValue = ta.atr(atrLength)
    atrPercent = 100.0 * atrValue / close
    regime: str = 'active' if atrPercent >= expansionPct else 'calm'
    weight = map.get(regimeWeight, regime)
    weightedDistance = (close - center) / atrValue * weight

    if ta.crossover(weightedDistance, 0.65):
        strategy.entry('Mosaic Long', strategy.long)
    if strategy.position_size > 0 and weightedDistance < -0.15:
        strategy.close('Mosaic Long', comment='Regime-adjusted trend failed')
    if strategy.position_size > 0:
        strategy.exit('Mosaic Guard', from_entry='Mosaic Long', stop=strategy.position_avg_price - atrValue * stopAtr / weight)

    plot(center, 'Regime Center', color=color.orange if regime == 'active' else color.teal)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
