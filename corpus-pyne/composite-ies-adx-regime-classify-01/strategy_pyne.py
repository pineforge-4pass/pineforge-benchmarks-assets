"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import high, input, low, math, script, strategy, ta
from pynecore.types import Series


@script.strategy("PF IES probe 01 - adx regime", shorttitle="IES_p01_REG", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_adx_len=input.int(14, "ADX Period", minval=5, maxval=30),
    i_adx_trend=input.float(25, "Trend Threshold", minval=15, maxval=40),
    i_atr_len=input.int(14, "ATR Period", minval=5, maxval=30),
    i_vol_exp=input.float(1.4, "Volatility Expansion", minval=1.1, maxval=2.0, step=0.1),
    i_vol_con=input.float(0.6, "Volatility Contraction", minval=0.3, maxval=0.9, step=0.1)
):

    def f_adx_calc(len: int):
        tr_val: float = ta.tr(True)
        plus_dm: float = math.max(high - high[1], 0)
        minus_dm: float = math.max(low[1] - low, 0)
        if plus_dm > minus_dm:
            minus_dm = 0
        else:
            plus_dm = 0
        smooth_tr: float = ta.rma(tr_val, len)
        smooth_plus: float = ta.rma(plus_dm, len)
        smooth_minus: float = ta.rma(minus_dm, len)
        plus_di: float = 100 * smooth_plus / smooth_tr if smooth_tr > 0 else 0
        minus_di: float = 100 * smooth_minus / smooth_tr if smooth_tr > 0 else 0
        di_sum: float = plus_di + minus_di
        dx: float = 100 * math.abs(plus_di - minus_di) / di_sum if di_sum > 0 else 0
        adx_val: float = ta.rma(dx, len)
        return (adx_val, plus_di, minus_di)

    adx, plus_di, minus_di = f_adx_calc(i_adx_len)

    atr_val: float = ta.atr(i_atr_len)
    atr_ma: float = ta.sma(atr_val, i_atr_len * 3)
    vol_ratio: float = atr_val / atr_ma if atr_ma > 0 else 1.0

    regime: int = 0
    if vol_ratio >= i_vol_exp and adx < i_adx_trend:
        regime = 3
    elif adx >= i_adx_trend:
        regime = 1
    elif vol_ratio <= i_vol_con:
        regime = 2

    trending_regime: Series[bool] = regime == 1

    long_entry: bool = trending_regime and (not trending_regime[1]) and (strategy.position_size == 0)
    long_exit: bool = not trending_regime and strategy.position_size > 0

    if long_entry:
        strategy.entry('L', strategy.long, qty=1, comment='trending ON')
    if long_exit:
        strategy.close('L', comment='trending OFF')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
