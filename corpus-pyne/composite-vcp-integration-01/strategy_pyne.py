"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    array, close, high, input, low, math, na, open, script, strategy, ta,
    time, timeframe, volume
)
from pynecore.types import Persistent, Series


@script.strategy("VCP probe 08 - integration", shorttitle="VCP_p08_INT", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False, max_boxes_count=300)
def main(
    i_pivot=input.int(5, "Pivot strength", minval=2, maxval=20),
    i_fvg_atr=input.float(0.3, "FVG min size (atr fraction)", minval=0.05, maxval=2.0, step=0.05),
    i_rsi_len=input.int(14, "RSI length", minval=5, maxval=30),
    i_vol_ma_len=input.int(20, "Volume MA length", minval=5, maxval=50),
    i_vol_z=input.float(2.0, "Volume z threshold", minval=1.0, maxval=4.0, step=0.1),
    i_cd_sum=input.int(10, "Cum-delta window", minval=2, maxval=50),
    i_adx_len=input.int(14, "ADX length", minval=5, maxval=30),
    i_adx_thr=input.float(25, "ADX trend threshold", minval=15, maxval=40),
    i_session=input.session("0800-1600", "Active session"),
    i_tz=input.string("America/New_York", "Timezone", options=("America/New_York", "Europe/London", "Asia/Tokyo", "UTC"))
):

    atr_v: float = ta.atr(14)

    ph_v: float = ta.pivothigh(high, i_pivot, i_pivot)
    pl_v: float = ta.pivotlow(low, i_pivot, i_pivot)

    last_ph: Persistent[float] = na(float)
    last_pl: Persistent[float] = na(float)
    if not na(ph_v):
        last_ph = ph_v
    if not na(pl_v):
        last_pl = pl_v

    pivot_break_up: bool = not na(last_ph) and close > last_ph
    pivot_break_dn: bool = not na(last_pl) and close < last_pl

    bull_fvg_event: bool = low > high[2] and close[1] > open[1]
    bear_fvg_event: bool = high < low[2] and close[1] < open[1]
    fvg_min_w: float = atr_v * i_fvg_atr

    z_top: Persistent[list[float]] = array.new_float()
    z_bot: Persistent[list[float]] = array.new_float()
    z_isb: Persistent[list[bool]] = array.new_bool()

    if bull_fvg_event and low - high[2] >= fvg_min_w:
        array.push(z_top, low)
        array.push(z_bot, high[2])
        array.push(z_isb, True)

    if bear_fvg_event and low[2] - high >= fvg_min_w:
        array.push(z_top, low[2])
        array.push(z_bot, high)
        array.push(z_isb, False)

    while array.size(z_top) > 30:
        array.shift(z_top)
        array.shift(z_bot)
        array.shift(z_isb)

    in_bull_fvg: bool = False
    in_bear_fvg: bool = False
    if array.size(z_top) > 0:
        for k in pine_range(0, array.size(z_top) - 1):
            t: float = array.get(z_top, k)
            b: float = array.get(z_bot, k)
            s: bool = array.get(z_isb, k)
            if low <= t and high >= b:
                if s:
                    in_bull_fvg = True
                else:
                    in_bear_fvg = True

    rsi_v: float = ta.rsi(close, i_rsi_len)
    rsi_smooth: Series[float] = ta.ema(rsi_v, 3)
    rsi_div_bull: bool = rsi_smooth < 40 and close > close[5] and (rsi_smooth > rsi_smooth[5])
    rsi_div_bear: bool = rsi_smooth > 60 and close < close[5] and (rsi_smooth < rsi_smooth[5])

    vol_ma: float = ta.sma(volume, i_vol_ma_len)
    vol_std: float = ta.stdev(volume, 20)
    vol_z: float = (volume - vol_ma) / vol_std if vol_std > 0 else 0
    vol_anom_bull: bool = math.abs(vol_z) > i_vol_z and close > open
    vol_anom_bear: bool = math.abs(vol_z) > i_vol_z and close < open

    buy_vol: float = volume if close > open else volume * (close - low) / (high - low + 0.0001)
    sell_vol: float = volume if close < open else volume * (high - close) / (high - low + 0.0001)
    vol_d: float = buy_vol - sell_vol
    cum_d: float = math.sum(vol_d, i_cd_sum)
    cd_up: bool = cum_d > 0
    cd_dn: bool = cum_d < 0

    up_mv: float = ta.change(high)
    dn_mv: float = -ta.change(low)
    p_dm_v: float = na if na(up_mv) else up_mv if up_mv > dn_mv and up_mv > 0 else 0
    m_dm_v: float = na if na(dn_mv) else dn_mv if dn_mv > up_mv and dn_mv > 0 else 0
    tr_smo: float = ta.rma(ta.tr, i_adx_len)
    p_di_v: float = 100 * ta.rma(p_dm_v, i_adx_len) / tr_smo if tr_smo > 0 else 0
    m_di_v: float = 100 * ta.rma(m_dm_v, i_adx_len) / tr_smo if tr_smo > 0 else 0
    dx_v: float = 100 * math.abs(p_di_v - m_di_v) / (p_di_v + m_di_v) if p_di_v + m_di_v > 0 else 0
    adx_v: float = ta.rma(dx_v, i_adx_len)
    trending_bull: bool = adx_v > i_adx_thr and p_di_v > m_di_v
    trending_bear: bool = adx_v > i_adx_thr and m_di_v > p_di_v

    in_session: Series[bool] = not na(time(timeframe.period, i_session, i_tz))

    long_setup: bool = pivot_break_up and in_bull_fvg and (vol_anom_bull or cd_up) and trending_bull and in_session

    short_setup: bool = pivot_break_dn and in_bear_fvg and (vol_anom_bear or cd_dn) and trending_bear and in_session

    if long_setup and strategy.position_size <= 0:
        if strategy.position_size < 0:
            strategy.close('S', comment='flip flat')
        strategy.entry('L', strategy.long, comment='vcp confluence long')

    if short_setup and strategy.position_size >= 0:
        if strategy.position_size > 0:
            strategy.close('L', comment='flip flat')
        strategy.entry('S', strategy.short, comment='vcp confluence short')

    if not in_session and in_session[1] and (strategy.position_size != 0):
        strategy.close_all(comment='session end')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
