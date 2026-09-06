"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, input, math, open, script, strategy, ta, volume


@script.strategy("VCP probe 04 - vol zscore anomaly", shorttitle="VCP_p04", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_vol_ma=input.int(20, "Volume MA Length", minval=5, maxval=50)
):

    volMA: float = ta.sma(volume, i_vol_ma)
    volStd: float = ta.stdev(volume, 20)
    volZ: float = (volume - volMA) / volStd
    volAnomaly: bool = math.abs(volZ) > 2.0

    if volAnomaly and close > open and (strategy.position_size == 0):
        strategy.entry('L', strategy.long, qty=1, comment='vol-z anomaly bull')

    if volAnomaly and close < open and (strategy.position_size > 0):
        strategy.close('L', comment='vol-z anomaly bear exit')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
