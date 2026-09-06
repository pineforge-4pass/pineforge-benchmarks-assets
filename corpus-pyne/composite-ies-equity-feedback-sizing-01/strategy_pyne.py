"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, hour, input, minute, na, script, strategy, ta
from pynecore.types import Persistent


@script.strategy("PF IES probe 08 - equity sizing", shorttitle="IES_p08_SIZE", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_risk_pct=input.float(1.0, "Risk Per Trade %", minval=0.1, maxval=5.0, step=0.1),
    i_atr_stop_mult=input.float(2.0, "ATR Stop Multiplier", minval=1.0, maxval=5.0, step=0.5),
    i_atr_tp_mult=input.float(4.0, "ATR Target Multiplier", minval=1.0, maxval=10.0, step=0.5),
    i_adx_trend=input.float(25, "ADX Trend Threshold", minval=15, maxval=40),
    i_trend_mult=input.float(1.2, "Trending Size Mult", minval=0.5, maxval=2.0, step=0.1),
    i_neutral_mult=input.float(1.0, "Neutral Size Mult", minval=0.5, maxval=2.0, step=0.1),
    i_quality_mult=input.float(1.15, "Quality Mult (fixed)", minval=1.0, maxval=1.5, step=0.05)
):

    plus_di, minus_di, adx_val = ta.dmi(14, 14)
    trending_regime: bool = adx_val >= i_adx_trend

    regime_size_mult: float = i_trend_mult if trending_regime else i_neutral_mult

    atr_val: float = ta.atr(14)
    long_risk: float = atr_val * i_atr_stop_mult

    account_risk: float = strategy.equity * (i_risk_pct / 100.0) * regime_size_mult * i_quality_mult
    long_position_size: float = account_risk / long_risk if long_risk > 0 else 0.0

    long_entry: bool = hour == 0 and minute == 15 and (strategy.position_size == 0) and (not na(atr_val)) and (not na(adx_val))

    entryStop: Persistent[float] = na(float)
    entryTP: Persistent[float] = na(float)

    if long_entry:
        entryStop = close - atr_val * i_atr_stop_mult
        entryTP = close + atr_val * i_atr_tp_mult
        strategy.entry('L', strategy.long, qty=long_position_size, comment='dyn qty long')
        strategy.exit('LX', 'L', stop=entryStop, limit=entryTP, comment='bracket')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
