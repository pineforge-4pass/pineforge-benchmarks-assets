"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, currency, high, input, low, math, script, strategy, ta
from pynecore.types import Persistent, Series


@script.strategy("PF IES probe 09 - integration", shorttitle="IES_p09_INT", overlay=True, initial_capital=1000000, currency=currency.USD, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_adx_len=input.int(14, "ADX period", minval=5, maxval=30),
    i_adx_trend=input.float(25, "ADX trend threshold", minval=15, maxval=40),
    i_atr_len=input.int(14, "ATR period", minval=5, maxval=30),
    i_vol_exp=input.float(1.4, "Vol expansion", minval=1.1, maxval=2.0, step=0.1),
    i_vol_con=input.float(0.6, "Vol contraction", minval=0.3, maxval=0.9, step=0.1),
    i_ma_fast=input.int(21, "Bias fast EMA", minval=5, maxval=50),
    i_ma_slow=input.int(55, "Bias slow EMA", minval=20, maxval=200),
    i_ma_trend=input.int(200, "Bias trend EMA", minval=50, maxval=500),
    i_bias_thresh=input.float(30, "Bias score threshold", minval=10, maxval=70),
    i_rsi_len=input.int(14, "RSI period", minval=5, maxval=30),
    i_rsi_bull=input.float(55, "RSI bullish level", minval=50, maxval=70),
    i_rsi_bear=input.float(45, "RSI bearish level", minval=30, maxval=50),
    i_macd_fast=input.int(12, "MACD fast", minval=5, maxval=20),
    i_macd_slow=input.int(26, "MACD slow", minval=15, maxval=50),
    i_macd_sig=input.int(9, "MACD signal", minval=3, maxval=15),
    i_press_len=input.int(14, "Pressure period", minval=5, maxval=50),
    i_press_smo=input.int(5, "Pressure smoothing", minval=1, maxval=20),
    i_press_mom=input.int(10, "Pressure momentum", minval=3, maxval=30),
    i_press_thr=input.float(0.05, "Pressure mom thresh", minval=0.01, maxval=0.2, step=0.01),
    i_cooldown=input.int(8, "Cooldown bars", minval=0, maxval=200)
):

    def f_adx_chain(len: int):
        tr_v: float = ta.tr(True)
        p_dm: float = math.max(high - high[1], 0)
        m_dm: float = math.max(low[1] - low, 0)
        if p_dm > m_dm:
            m_dm = 0
        else:
            p_dm = 0
        s_tr: float = ta.rma(tr_v, len)
        s_p: float = ta.rma(p_dm, len)
        s_m: float = ta.rma(m_dm, len)
        p_di_v: float = 100 * s_p / s_tr if s_tr > 0 else 0
        m_di_v: float = 100 * s_m / s_tr if s_tr > 0 else 0
        di_sum: float = p_di_v + m_di_v
        dx_v: float = 100 * math.abs(p_di_v - m_di_v) / di_sum if di_sum > 0 else 0
        adx_v: float = ta.rma(dx_v, len)
        return (adx_v, p_di_v, m_di_v)

    adx_v, p_di_v, m_di_v = f_adx_chain(i_adx_len)
    atr_v: float = ta.atr(i_atr_len)
    atr_avg: float = ta.sma(atr_v, i_atr_len * 3)
    vol_ratio: float = atr_v / atr_avg if atr_avg > 0 else 1.0

    regime: int = 0
    if vol_ratio >= i_vol_exp and adx_v < i_adx_trend:
        regime = 3
    elif adx_v >= i_adx_trend:
        regime = 1
    elif vol_ratio <= i_vol_con:
        regime = 2

    trending: bool = regime == 1
    di_bull: bool = p_di_v > m_di_v
    di_bear: bool = m_di_v > p_di_v

    ma_fast: float = ta.ema(close, i_ma_fast)
    ma_slow: float = ta.ema(close, i_ma_slow)
    ma_trend: float = ta.ema(close, i_ma_trend)

    stack_up: bool = ma_fast > ma_slow and ma_slow > ma_trend
    stack_dn: bool = ma_fast < ma_slow and ma_slow < ma_trend
    above_str: bool = close > ma_fast and close > ma_slow
    below_str: bool = close < ma_fast and close < ma_slow

    bull_bias: float = 0.0
    if stack_up:
        bull_bias += 30
    if above_str:
        bull_bias += 20
    if close > ma_trend:
        bull_bias += 20

    bear_bias: float = 0.0
    if stack_dn:
        bear_bias += 30
    if below_str:
        bear_bias += 20
    if close < ma_trend:
        bear_bias += 20

    bias_bull: bool = bull_bias >= i_bias_thresh
    bias_bear: bool = bear_bias >= i_bias_thresh

    rsi_v: Series[float] = ta.rsi(close, i_rsi_len)
    rsi_bull: bool = rsi_v > i_rsi_bull
    rsi_bear: bool = rsi_v < i_rsi_bear
    rsi_mom_up: bool = rsi_v > rsi_v[3]
    rsi_mom_dn: bool = rsi_v < rsi_v[3]

    macd_line: float = ta.ema(close, i_macd_fast) - ta.ema(close, i_macd_slow)
    macd_sig: float = ta.ema(macd_line, i_macd_sig)
    macd_hist: Series[float] = macd_line - macd_sig
    macd_bull: bool = macd_hist > 0 and macd_hist > macd_hist[1]
    macd_bear: bool = macd_hist < 0 and macd_hist < macd_hist[1]

    mom_bull: int = 0
    if rsi_bull:
        mom_bull += 1
    if rsi_mom_up:
        mom_bull += 1
    if macd_bull:
        mom_bull += 1

    mom_bear: int = 0
    if rsi_bear:
        mom_bear += 1
    if rsi_mom_dn:
        mom_bear += 1
    if macd_bear:
        mom_bear += 1

    mom_bull_ok: bool = mom_bull >= 2
    mom_bear_ok: bool = mom_bear >= 2

    bar_range: float = high - low
    raw_press: float = (close - low) / bar_range if bar_range > 0 else 0.5
    press_r: float = ta.ema(raw_press, i_press_len)
    press_s: Series[float] = ta.ema(press_r, i_press_smo)
    press_mom: float = press_s - press_s[i_press_mom]

    press_bull: bool = press_s > 0.5 + i_press_thr or press_mom > i_press_thr
    press_bear: bool = press_s < 0.5 - i_press_thr or press_mom < -i_press_thr

    bull_total: int = 0
    if trending and di_bull:
        bull_total += 2
    if bias_bull:
        bull_total += 1
    if mom_bull_ok:
        bull_total += 1
    if press_bull:
        bull_total += 1

    bear_total: int = 0
    if trending and di_bear:
        bear_total += 2
    if bias_bear:
        bear_total += 1
    if mom_bear_ok:
        bear_total += 1
    if press_bear:
        bear_total += 1

    bars_since_trade: Persistent[int] = 999
    bars_since_trade = bars_since_trade + 1
    cooldown_ok: bool = bars_since_trade >= i_cooldown

    long_entry: bool = bull_total >= 5 and trending and cooldown_ok and (strategy.position_size <= 0)
    short_entry: bool = bear_total >= 5 and trending and cooldown_ok and (strategy.position_size >= 0)

    if long_entry:
        if strategy.position_size < 0:
            strategy.close('S', comment='flip')
        strategy.entry('L', strategy.long, comment='composite long')
        bars_since_trade = 0

    if short_entry:
        if strategy.position_size > 0:
            strategy.close('L', comment='flip')
        strategy.entry('S', strategy.short, comment='composite short')
        bars_since_trade = 0

    if not trending and strategy.position_size != 0:
        strategy.close_all(comment='regime exit')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
