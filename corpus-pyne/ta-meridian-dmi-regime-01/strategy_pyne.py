"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, display, input, plot, script, strategy, ta


@script.strategy("PineForge — Meridian DMI Regime", overlay=True, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=2, pyramiding=0, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, margin_long=100, margin_short=100, process_orders_on_close=False, calc_on_order_fills=False)
def main(
    diLength=input.int(14, "DI Length", minval=2, group="Signal"),
    adxSmoothing=input.int(12, "ADX Smoothing", minval=2, group="Signal"),
    trendLength=input.int(48, "Trend EMA", minval=5, group="Signal"),
    entryStrength=input.float(19.0, "Entry ADX", minval=5, maxval=60, step=0.5, group="Signal"),
    exitStrength=input.float(14.0, "Exit ADX", minval=5, maxval=50, step=0.5, group="Signal"),
    atrLength=input.int(18, "ATR Length", minval=2, group="Risk"),
    stopAtr=input.float(2.2, "Stop ATR", minval=0.5, step=0.1, group="Risk")
):
    positiveDi, negativeDi, adxValue = ta.dmi(diLength, adxSmoothing)
    trend = ta.ema(close, trendLength)
    atrValue = ta.atr(atrLength)

    entrySignal = ta.crossover(positiveDi, negativeDi) and adxValue > entryStrength and (close > trend)
    exitSignal = ta.crossunder(positiveDi, negativeDi) or adxValue < exitStrength or close < trend

    if entrySignal:
        strategy.entry('Meridian Long', strategy.long)

    if strategy.position_size > 0 and exitSignal:
        strategy.close('Meridian Long', comment='Directional regime ended')

    if strategy.position_size > 0:
        strategy.exit('Meridian Guard', from_entry='Meridian Long', stop=strategy.position_avg_price - atrValue * stopAtr)

    plot(trend, 'Trend EMA', color=color.orange)
    plot(adxValue, 'ADX', color=color.purple, display=display.data_window)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
