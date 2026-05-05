"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, currency, fill, format, high, input, location, low, math,
    na, nz, open, plot, plotshape, position, script, shape, size, strategy, string, ta, table,
    text
)
from pynecore.types import Color, Persistent, PersistentSeries, Series, Table


@script.strategy("Canuck Trading KAMA Strategy", shorttitle="CT_KAMA", overlay=True, calc_on_every_tick=True, max_bars_back=500, use_bar_magnifier=False, initial_capital=1000000, currency=currency.USD, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    input_direction=input.string("Long", "Trade Direction", options=("Long", "Short", "Both"), group="Strategy", tooltip="Long = longs only. Short = shorts only. Both = full reversal."),
    input_trade_mode=input.string("Hold", "Trade Behaviour", options=("Hold", "Exit", "Adaptive"), group="Strategy", tooltip="Hold = hold through gray, exit only on opposite color. Exit = close position when color turns gray. Adaptive = dynamically scale position size based on band extension and trend quality."),
    input_use_dev_gate=input.bool(True, "Band Deviation Gate", group="Strategy", tooltip="When enabled, entries are blocked if price is more than Max Entry Deviation σ from fair value."),
    input_max_dev=input.float(1.5, "Max Entry Deviation (σ)", minval=0.1, maxval=5.0, step=0.1, group="Strategy", tooltip="Maximum σ distance from KAMA to allow new entries. Default 1.5σ."),
    input_trim_start=input.float(1.0, "Trim Start (σ)", minval=0.3, maxval=3.0, step=0.1, group="Adaptive", tooltip="σ distance from KAMA where position trimming begins. Default 1.0σ."),
    input_trim_step=input.float(20.0, "Trim Step (%)", minval=5.0, maxval=50.0, step=5.0, group="Adaptive", tooltip="Percentage of original position to trim at each σ threshold. Default 20%."),
    input_min_hold=input.float(25.0, "Min Hold (%)", minval=10.0, maxval=75.0, step=5.0, group="Adaptive", tooltip="Minimum position size as % of original. Never trim below this floor. Default 25%."),
    input_reload_buf=input.float(0.5, "Reload Buffer", minval=0.1, maxval=1.0, step=0.1, group="Adaptive", tooltip="Reload triggers at this fraction of the trim distance. 0.5 = reload halfway back. Default 0.5."),
    input_trend_shift=input.float(0.5, "Trend Quality Shift (σ)", minval=0.0, maxval=2.0, step=0.1, group="Adaptive", tooltip="In strong trends (high ER + acceleration), trim thresholds shift out by this amount. Default 0.5σ."),
    input_cooldown=input.int(2, "Cooldown (bars)", minval=0, maxval=10, group="Adaptive", tooltip="Minimum bars between adaptive trim/reload actions. Prevents churning. Default 2."),
    input_er_len=input.int(10, "ER Length", minval=2, maxval=50, group="KAMA Engine", tooltip="Efficiency Ratio lookback period. Higher = smoother, slower to react. Default 10."),
    input_fast_period=input.int(2, "Fast Period", minval=2, maxval=10, group="KAMA Engine", tooltip="KAMA fast smoothing constant period. Lower = faster response in trends. Default 2."),
    input_slow_period=input.int(30, "Slow Period", minval=10, maxval=100, group="KAMA Engine", tooltip="KAMA slow smoothing constant period. Higher = more filtering in chop. Default 30."),
    input_dev_len=input.int(20, "Deviation Length", minval=5, maxval=100, group="KAMA Engine", tooltip="Lookback for band deviation calculation. Default 20."),
    input_band_mult=input.float(2.0, "Band Multiplier", minval=0.5, maxval=5.0, step=0.25, group="KAMA Engine", tooltip="Band width as multiple of standard deviation from KAMA. Default 2.0."),
    input_col_bull=input.color(color.new('#00E676'), "Trending Up", group="Style"),
    input_col_bear=input.color(color.new('#FF1744'), "Trending Down", group="Style"),
    input_col_neutral=input.color(color.new('#787B86'), "Coiling", group="Style"),
    input_col_band=input.color(color.new('#2962FF'), "Bands", group="Style"),
    input_kama_width=input.int(3, "Fair Value Line Width", minval=1, maxval=5, group="Style"),
    input_show_dash=input.bool(True, "Show Dashboard", group="Display"),
    input_dash_pos=input.string("Top Right", "Position", options=("Top Right", "Top Left", "Bottom Right", "Bottom Left", "Middle Right", "Middle Left"), group="Display"),
    input_dash_size=input.string("Small", "Text Size", options=("Tiny", "Small", "Normal"), group="Display"),
    input_show_bands=input.bool(True, "Show Bands", group="Display"),
    input_show_sigs=input.bool(True, "Show Signals", group="Display"),
    input_th_accent=input.color(color.new('#FF9800'), "Accent", group="Theme"),
    input_th_label=input.color(color.new('#787B86'), "Labels", group="Theme"),
    input_th_hdr_bg=input.color(color.new('#0D1117'), "Header Background", group="Theme"),
    input_th_bg1=input.color(color.new('#131722'), "Row Background", group="Theme"),
    input_th_bg2=input.color(color.new('#1E222D'), "Alt Background", group="Theme"),
    input_th_border=input.color(color.new('#363A45'), "Border", group="Theme")
):




    ER_LEN: int = input_er_len
    FAST_PERIOD: int = input_fast_period
    SLOW_PERIOD: int = input_slow_period
    DEV_LEN: int = input_dev_len
    BAND_MULT: float = input_band_mult

    net_move: float = math.abs(close - close[ER_LEN])
    total_path: float = math.sum(math.abs(close - close[1]), ER_LEN)
    er: Series[float] = net_move / total_path if total_path != 0.0 else 0.0

    fast_sc: float = 2.0 / (FAST_PERIOD + 1)
    slow_sc: float = 2.0 / (SLOW_PERIOD + 1)
    sc: float = math.pow(er * (fast_sc - slow_sc) + slow_sc, 2)

    kama: PersistentSeries[float] = na(float)
    kama = close if na(kama[1]) else kama[1] + sc * (close - kama[1])

    kama_dev: float = math.sqrt(ta.sma(math.pow(close - kama, 2), DEV_LEN))
    band_upper: float = kama + BAND_MULT * kama_dev
    band_lower: float = kama - BAND_MULT * kama_dev
    band_width: float = band_upper - band_lower
    band_pos: float = (close - band_lower) / band_width if band_width > 0.0 else 0.5
    in_lower_z: bool = band_pos <= 0.33
    in_upper_z: bool = band_pos >= 0.67
    in_mid_z: bool = not in_lower_z and (not in_upper_z)

    bw_pct: float = band_width / kama * 100.0 if kama > 0.0 else 0.0
    bw_avg: float = ta.sma(bw_pct, DEV_LEN)
    bw_ratio: float = bw_pct / bw_avg if nz(bw_avg) > 0.0 else 1.0
    bwr_long_avg: float = ta.ema(bw_ratio, DEV_LEN * 2)
    bwr_dev: float = ta.ema(math.abs(bw_ratio - bwr_long_avg), DEV_LEN)
    volatile_mkt: bool = bw_ratio > bwr_long_avg + bwr_dev
    tight_coil: bool = bw_ratio < bwr_long_avg - bwr_dev

    dist_from_fv_norm: float = (close - kama) / kama_dev if kama_dev > 0.0 else 0.0
    abs_dist: float = math.abs(dist_from_fv_norm)

    sc_threshold: float = math.sqrt(math.pow(slow_sc, 2) * math.pow(fast_sc, 2))
    is_choppy: bool = sc < sc_threshold

    kama_slope_raw: float = kama - kama[1]
    kama_slope: Series[float] = ta.ema(kama_slope_raw, 3)
    slope_accel: Series[bool] = kama_slope > kama_slope[1]

    is_green: bool = not is_choppy and kama_slope > 0.0 and (slope_accel or slope_accel[1]) and (close > kama)
    is_red: bool = not is_choppy and kama_slope < 0.0 and (not slope_accel) and (not slope_accel[1]) and (close < kama)
    is_gray: Series[bool] = not is_green and (not is_red)

    er_avg: float = ta.ema(er, DEV_LEN)
    er_change_rate: float = ta.ema(math.abs(er - er[1]), 5)
    er_noise_floor: float = math.max(er_avg * 0.6, 0.1)
    er_strong_thresh: float = math.min(er_avg + er_change_rate * 4.0, 0.85)
    er_rising: bool = er > er[1]
    er_slope: float = ta.ema(er - er[3], 3)
    er_building: bool = er_slope > 0.0 and er > er_noise_floor
    coil_ratio: float = math.sum(1 if is_gray else 0, ER_LEN) / ER_LEN
    mostly_coiling: bool = coil_ratio > 0.5

    strong_trend: bool = er >= er_strong_thresh and slope_accel

    body_size: float = math.abs(close - open)
    full_range: float = high - low
    body_ratio: float = body_size / full_range if full_range > 0.0 else 0.5
    upper_wick: float = high - math.max(open, close)
    lower_wick: float = math.min(open, close) - low
    wick_ratio_upper: float = upper_wick / full_range if full_range > 0.0 else 0.0
    wick_ratio_lower: float = lower_wick / full_range if full_range > 0.0 else 0.0
    rejection_top: bool = wick_ratio_upper > 0.4 and in_upper_z
    rejection_bottom: bool = wick_ratio_lower > 0.4 and in_lower_z

    in_long: Series[bool] = strategy.position_size > 0
    in_short: Series[bool] = strategy.position_size < 0
    in_trade: bool = in_long or in_short
    flat: bool = not in_trade

    long_goes_gray: bool = in_long and is_gray and (not is_gray[1])
    short_goes_gray: bool = in_short and is_gray and (not is_gray[1])
    long_goes_red: bool = in_long and is_red
    short_goes_green: bool = in_short and is_green

    new_position: bool = in_long and (not in_long[1]) or (in_short and (not in_short[1]))

    original_qty: Persistent[float] = na(float)
    peak_sigma: Persistent[float] = 0.0
    current_pct: Persistent[float] = 1.0
    bars_since_adj: Persistent[int] = 0
    last_adapt_action: Persistent[str] = "NONE"

    if new_position:
        original_qty = math.abs(strategy.position_size)
        peak_sigma = abs_dist
        current_pct = 1.0
        bars_since_adj = 0
        last_adapt_action = "ENTRY"

    if flat:
        original_qty = na
        peak_sigma = 0.0
        current_pct = 1.0
        bars_since_adj = 0
        last_adapt_action = "NONE"

    if in_trade and (not new_position):
        bars_since_adj += 1
        if abs_dist > peak_sigma:
            peak_sigma = abs_dist

    dev_ok: bool = not input_use_dev_gate or abs_dist <= input_max_dev

    if input_trade_mode == 'Hold':
        if long_goes_red:
            strategy.close('Long', comment='Color Ended')
        if short_goes_green:
            strategy.close('Short', comment='Color Ended')

    if input_trade_mode == 'Exit':
        if in_long and (not is_green):
            strategy.close('Long', comment='Color Ended')
        if in_short and (not is_red):
            strategy.close('Short', comment='Color Ended')

    if input_trade_mode == 'Adaptive' and in_trade and (not new_position):
        if long_goes_red:
            strategy.close('Long', comment='Color Ended')
            last_adapt_action = "EXIT"
        elif short_goes_green:
            strategy.close('Short', comment='Color Ended')
            last_adapt_action = "EXIT"
        elif not na(original_qty) and original_qty > 0:
            _shift: float = input_trend_shift if strong_trend else 0.0

            _pa_shift: float = -0.25 if in_long and rejection_top or (in_short and rejection_bottom) else 0.0
            _eff_shift: float = math.max(_shift + _pa_shift, 0.0)

            _gray_penalty: float = 0.25 if is_gray else 0.0

            _trim_thresh: float = input_trim_start + _eff_shift - _gray_penalty
            _step_frac: float = input_trim_step / 100.0
            _min_frac: float = input_min_hold / 100.0
            _cooldown_ok: bool = bars_since_adj >= input_cooldown

            _trim_depth: float = (abs_dist - _trim_thresh) / math.max(_trim_thresh * 0.5, 0.25) if abs_dist > _trim_thresh else 0.0
            _trim_frac: float = math.min(_trim_depth * _step_frac, 1.0 - _min_frac)
            _target_pct: float = math.max(1.0 - _trim_frac, _min_frac)

            _reload_thresh: float = peak_sigma * input_reload_buf
            _color_ok: bool = in_long and is_green or (in_short and is_red)
            _reload_zone: bool = abs_dist < _reload_thresh and _color_ok
            if _reload_zone:
                _target_pct = math.max(_target_pct, math.min(current_pct + _step_frac, 1.0))

            _pct_diff: float = _target_pct - current_pct
            _sig_change: bool = math.abs(_pct_diff) >= _step_frac * 0.5

            if _cooldown_ok and _sig_change:
                _target_qty: float = math.max(original_qty * _target_pct, 1.0)
                _current_qty: float = math.abs(strategy.position_size)
                _delta: float = _target_qty - _current_qty

                if _delta < 0 and math.abs(_delta) >= 1.0:
                    strategy.close('Long' if in_long else 'Short', qty=math.abs(_delta), comment='Adapt Trim')
                    current_pct = _target_pct
                    bars_since_adj = 0
                    last_adapt_action = "TRIM"
                elif _delta > 0 and _color_ok and dev_ok:
                    strategy.order('Long' if in_long else 'Short', strategy.long if in_long else strategy.short, qty=_delta, comment='Adapt Reload')
                    current_pct = _target_pct
                    bars_since_adj = 0
                    last_adapt_action = "RELOAD"

    color_long: bool = flat and is_green and dev_ok and (input_direction != 'Short')
    color_short: bool = flat and is_red and dev_ok and (input_direction != 'Long')

    if color_long:
        strategy.entry('Long', strategy.long, comment='Trend Long')
    if color_short:
        strategy.entry('Short', strategy.short, comment='Trend Short')

    any_long_entry: bool = color_long
    any_short_entry: bool = color_short

    entry_close: Persistent[float] = na(float)
    if new_position:
        entry_close = close[1]

    sigma_moved: float = (close - entry_close) / math.max(kama_dev, 1e-10) if in_long else (entry_close - close) / math.max(kama_dev, 1e-10) if in_short else 0.0

    pos_age: Persistent[int] = 0
    if new_position:
        pos_age = 1
    elif in_trade:
        pos_age += 1
    else:
        pos_age = 0

    state_color: Color = input_col_bull if is_green else input_col_bear if is_red else input_col_neutral
    p_kama = plot(kama, 'Fair Value', state_color, linewidth=input_kama_width)

    band_color: Color = color.new(input_col_band, 65) if input_show_bands else na
    p_up = plot(band_upper, 'Upper Band', band_color, linewidth=1)
    p_dn = plot(band_lower, 'Lower Band', band_color, linewidth=1)
    fill(p_kama, p_up, color=na, title='Upper Zone')
    fill(p_kama, p_dn, color=na, title='Lower Zone')

    plotshape(any_long_entry and input_show_sigs, 'Buy', shape.triangleup, location.belowbar, input_col_bull, size=size.tiny)
    plotshape(any_short_entry and input_show_sigs, 'Sell', shape.triangledown, location.abovebar, input_col_bear, size=size.tiny)

    __switch__ = input_dash_pos
    if __switch__ == "Top Right":
        __block_result__ = position.top_right
    elif __switch__ == "Top Left":
        __block_result__ = position.top_left
    elif __switch__ == "Bottom Right":
        __block_result__ = position.bottom_right
    elif __switch__ == "Bottom Left":
        __block_result__ = position.bottom_left
    elif __switch__ == "Middle Right":
        __block_result__ = position.middle_right
    elif __switch__ == "Middle Left":
        __block_result__ = position.middle_left
    else:
        __block_result__ = position.top_right
    _dash_pos: str = __block_result__

    __switch__ = input_dash_size
    if __switch__ == "Tiny":
        __block_result__ = size.tiny
    elif __switch__ == "Normal":
        __block_result__ = size.normal
    else:
        __block_result__ = size.small
    _sz: str = __block_result__

    __switch__ = input_dash_size
    if __switch__ == "Tiny":
        __block_result__ = size.tiny
    elif __switch__ == "Normal":
        __block_result__ = size.small
    else:
        __block_result__ = size.small
    _hdr_sz: str = __block_result__

    dash: Persistent[Table] = na(Table)
    if input_show_dash:
        if na(dash):
            dash = table.new(_dash_pos, columns=2, rows=11, bgcolor=color.new(input_th_bg1, 0), border_width=1, border_color=color.new(input_th_border, 30), frame_width=2, frame_color=color.new(input_th_border, 0))

        _bg0: Color = color.new(input_th_hdr_bg, 0)
        _bg1: Color = color.new(input_th_bg1, 0)
        _bg2: Color = color.new(input_th_bg2, 0)
        _lbl: Color = input_th_label
        _acc: Color = input_th_accent

        _live: bool = strategy.position_size != 0
        _pnl: float = strategy.openprofit
        _avg: float = strategy.position_avg_price
        _pnl_pct: float = (close / _avg - 1.0) * 100.0 * (1.0 if in_long else -1.0) if _avg > 0.0 and _live else 0.0

        table.cell(dash, 0, 0, 'CT KAMA', text_color=_acc, text_size=_hdr_sz, text_halign=text.align_left, bgcolor=_bg0)
        table.cell(dash, 1, 0, 'v8.0', text_color=_lbl, text_size=_hdr_sz, text_halign=text.align_right, bgcolor=_bg0)

        table.cell(dash, 0, 1, 'Price', text_color=_lbl, text_size=_sz, text_halign=text.align_left, bgcolor=_bg1)
        table.cell(dash, 1, 1, string.tostring(close, format.mintick), text_color=color.white, text_size=_sz, text_halign=text.align_right, bgcolor=_bg1)

        table.cell(dash, 0, 2, 'Fair Value', text_color=_lbl, text_size=_sz, text_halign=text.align_left, bgcolor=_bg2)
        table.cell(dash, 1, 2, string.tostring(kama, format.mintick), text_color=state_color, text_size=_sz, text_halign=text.align_right, bgcolor=_bg2)

        _state_t: str = '▲ TRENDING UP' if is_green else '▼ TRENDING DOWN' if is_red else '◈ COILING TIGHT' if tight_coil else '◈ COILING'
        _state_c: Color = input_col_bull if is_green else input_col_bear if is_red else input_col_band if tight_coil else input_col_neutral
        table.cell(dash, 0, 3, 'Market', text_color=_lbl, text_size=_sz, text_halign=text.align_left, bgcolor=_bg1)
        table.cell(dash, 1, 3, _state_t, text_color=_state_c, text_size=_sz, text_halign=text.align_right, bgcolor=_bg1)

        _h_in: bool = in_long or in_short
        _sig_t: str = '✕ COLOR ENDED' if long_goes_red or short_goes_green else '✕ COLOR ENDED' if (long_goes_gray or short_goes_gray) and input_trade_mode == 'Exit' else '▲ TREND LONG' if color_long else '▼ TREND SHORT' if color_short else '◑ ADAPT TRIM' if _h_in and last_adapt_action == 'TRIM' and (bars_since_adj < 2) else '▲ ADAPT RELOAD' if _h_in and last_adapt_action == 'RELOAD' and (bars_since_adj < 2) else '● GREEN — WATCHING' if is_green else '● RED — WATCHING' if is_red else '◈ GRAY — HOLDING' if _h_in and is_gray else '◈ GRAY'
        _sig_c: Color = input_col_bear if long_goes_red or short_goes_green else input_col_bear if (long_goes_gray or short_goes_gray) and input_trade_mode == 'Exit' else input_col_bull if color_long else input_col_bear if color_short else _acc if _h_in and last_adapt_action == 'TRIM' and (bars_since_adj < 2) else input_col_bull if _h_in and last_adapt_action == 'RELOAD' and (bars_since_adj < 2) else input_col_bull if is_green else input_col_bear if is_red else _acc if _h_in and is_gray else _lbl
        table.cell(dash, 0, 4, 'Signal', text_color=_lbl, text_size=_sz, text_halign=text.align_left, bgcolor=_bg2)
        table.cell(dash, 1, 4, _sig_t, text_color=_sig_c, text_size=_sz, text_halign=text.align_right, bgcolor=_bg2)

        _pos_val: float = math.abs(strategy.position_size) * close
        _pos_pct: float = _pos_val / strategy.equity * 100.0 if strategy.equity > 0 else 0.0
        _pos_t: str = '● LONG  ' + string.tostring(strategy.position_size, '#.##') + '  $' + string.tostring(_pos_val, '#,###.##') + ' (' + string.tostring(_pos_pct, '#.#') + '%)' if in_long else '● SHORT  ' + string.tostring(math.abs(strategy.position_size), '#.##') + '  $' + string.tostring(_pos_val, '#,###.##') + ' (' + string.tostring(_pos_pct, '#.#') + '%)' if in_short else '─'
        _pos_c: Color = input_col_bull if in_long else input_col_bear if in_short else _lbl
        table.cell(dash, 0, 5, 'Position', text_color=_lbl, text_size=_sz, text_halign=text.align_left, bgcolor=_bg1)
        table.cell(dash, 1, 5, _pos_t, text_color=_pos_c, text_size=_sz, text_halign=text.align_right, bgcolor=_bg1)

        _pnl_pfx: str = '+' if _pnl >= 0.0 else ''
        _pnl_t: str = _pnl_pfx + string.tostring(_pnl, '#.##') + '  (' + string.tostring(_pnl_pct, '#.##') + '%)' if _live else '─'
        _pnl_c: Color = input_col_bull if _pnl > 0.0 else input_col_bear if _pnl < 0.0 else _lbl
        table.cell(dash, 0, 6, 'P&L', text_color=_lbl, text_size=_sz, text_halign=text.align_left, bgcolor=_bg2)
        table.cell(dash, 1, 6, _pnl_t, text_color=_pnl_c if _live else _lbl, text_size=_sz, text_halign=text.align_right, bgcolor=_bg2)

        _er_c: Color = input_col_bull if er >= er_strong_thresh else _acc if er >= er_noise_floor else input_col_bear
        _er_l: str = 'TRENDING' if er >= er_strong_thresh else 'BUILDING' if er >= er_noise_floor else 'COILING'
        _cr_t: str = '  COIL ' + string.tostring(coil_ratio * 100.0, '#') + '%' if mostly_coiling else ''
        table.cell(dash, 0, 7, 'ER', text_color=_lbl, text_size=_sz, text_halign=text.align_left, bgcolor=_bg1)
        table.cell(dash, 1, 7, string.tostring(er, '#.###') + (' ◆ ' if er_rising else ' ◇ ') + _er_l + _cr_t, text_color=_er_c, text_size=_sz, text_halign=text.align_right, bgcolor=_bg1)

        _zone_t: str = 'LOWER' if in_lower_z else 'UPPER' if in_upper_z else 'MID'
        _vol_t: str = 'VOLATILE' if volatile_mkt else 'TIGHT COIL' if tight_coil else ''
        _bnd_t: str = string.tostring(band_pos, '#.##') + ' ' + _zone_t + ('  ' + _vol_t if _vol_t != '' else '')
        _bnd_c: Color = input_col_bear if volatile_mkt else input_col_band if tight_coil else _acc if in_mid_z else input_col_band
        table.cell(dash, 0, 8, 'Band', text_color=_lbl, text_size=_sz, text_halign=text.align_left, bgcolor=_bg2)
        table.cell(dash, 1, 8, _bnd_t, text_color=_bnd_c, text_size=_sz, text_halign=text.align_right, bgcolor=_bg2)

        _dev_t: str = string.tostring(sigma_moved, '#.##') + 'σ  age:' + string.tostring(pos_age) + '  dist:' + string.tostring(dist_from_fv_norm, '#.##') + 'σ' if _h_in else '─'
        _dev_thresh: float = input_max_dev if input_use_dev_gate else 1.5
        _dev_c: Color = _lbl if not _h_in else _acc if abs_dist > _dev_thresh else _lbl
        table.cell(dash, 0, 9, 'Dev', text_color=_lbl, text_size=_sz, text_halign=text.align_left, bgcolor=_bg1)
        table.cell(dash, 1, 9, _dev_t, text_color=_dev_c, text_size=_sz, text_halign=text.align_right, bgcolor=_bg1)

        _adp_t: str = "─"
        _adp_c: Color = _lbl
        if input_trade_mode == 'Adaptive' and _h_in:
            _act_t: str = last_adapt_action
            _adp_t = string.tostring(current_pct * 100.0, '#') + '%  pk:' + string.tostring(peak_sigma, '#.##') + 'σ  ' + _act_t
            _adp_c = input_col_bull if current_pct >= 0.9 else _acc if current_pct >= 0.5 else input_col_bear
        table.cell(dash, 0, 10, 'Adaptive', text_color=_lbl, text_size=_sz, text_halign=text.align_left, bgcolor=_bg2)
        table.cell(dash, 1, 10, _adp_t, text_color=_adp_c, text_size=_sz, text_halign=text.align_right, bgcolor=_bg2)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)