"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, barcolor, chart, close, color, currency, format, high, hour,
    input, label, low, minute, na, open, plot, plotcandle, script, strategy, string, ta, volume
)
from pynecore.types import Color, NA, Persistent, PersistentSeries, Series


@script.strategy("Market Shift Levels + 152MA Strategy - v2", overlay=True, use_bar_magnifier=False, initial_capital=1000000, currency=currency.USD, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    length=input.int(55, "Market Shift Length"),
    __input_1__=input.string("Volume", "Label Data: ", ("Volume", "Price")),
    color_shiftUp=input.color(color.rgb(36, 213, 128), "Shift Up Color", inline="col"),
    color_shiftDn=input.color(color.rgb(225, 43, 43), "Shift Down Color", inline="col"),
    allow_overnight=input.bool(False, "Allow Overnight Position")
):
    lbl_data: bool = __input_1__ == 'Volume'

    ma_period: int = 152

    close_hour: int = 4
    close_minute: int = 55

    able_to_trade: bool = True

    level: Persistent = NA(float)
    hma1: Series[float] = ta.hma(close, length)
    hma2: float = hma1[5]
    vol_sum: float = volume[2] + volume[1] + volume

    if ta.crossover(hma1, hma2):
        level = low
    if ta.crossunder(hma1, hma2):
        level = high

    is_green_bar: PersistentSeries[bool] = False
    is_red_bar: PersistentSeries[bool] = False
    is_below_sma: Persistent[bool] = False
    is_above_sma: Persistent[bool] = False

    sma152: Series[float] = ta.sma(close, ma_period)

    is_red_bar = close < level
    is_green_bar = not is_red_bar

    is_below_sma = close < sma152
    is_above_sma = not is_below_sma

    shift_col: Color = color_shiftDn if is_red_bar else color_shiftUp

    is_close_time: bool = False
    if not allow_overnight:
        is_close_time = hour == close_hour and minute >= close_minute

    if is_close_time and strategy.position_size != 0:
        if strategy.position_size > 0:
            strategy.close('Long', comment='Daily Close', alert_message='long_exit')
        elif strategy.position_size < 0:
            strategy.close('Short', comment='Daily Close', alert_message='short_exit')

    if strategy.position_size > 0 and is_red_bar and (close < strategy.position_avg_price):
        strategy.close('Long', comment='紅棒且低於入場價', alert_message='long_exit')

    if strategy.position_size > 0 and is_red_bar and is_below_sma:
        strategy.close('Long', comment='紅棒且低於SMA152', alert_message='long_exit')

    if strategy.position_size > 0:
        if is_green_bar[1] and is_green_bar[2] and (close[1] < sma152[1]):
            if is_red_bar:
                strategy.close('Long', comment='連續綠棒且低於SMA152，且紅棒', alert_message='long_exit')

    if strategy.position_size < 0 and is_green_bar and (close > strategy.position_avg_price):
        strategy.close('Short', comment='綠棒且高於入場價', alert_message='short_exit')

    if strategy.position_size < 0 and is_green_bar and is_above_sma:
        strategy.close('Short', comment='綠棒且高於SMA152', alert_message='short_exit')

    if strategy.position_size < 0:
        if is_red_bar and is_red_bar[1] and (close[1] > sma152[1]):
            if is_green_bar:
                strategy.close('Short', comment='連續紅棒且高於SMA152，且綠棒', alert_message='short_exit')

    long_entry: bool = is_green_bar and is_above_sma
    if long_entry and strategy.position_size <= 0:
        if strategy.position_size < 0:
            strategy.close('Short', alert_message='short_exit')
        strategy.entry('Long', strategy.long, alert_message='long_entry')

    short_entry: bool = is_red_bar and is_below_sma
    if short_entry and strategy.position_size >= 0:
        if strategy.position_size > 0:
            strategy.close('Long', alert_message='long_exit')
        strategy.entry('Short', strategy.short, alert_message='short_entry')

    plot(level, 'Market Shift Levels', color=chart.fg_color, style=plot.style_linebr)

    plot(sma152, 'SMA 152', color=color.yellow, linewidth=2)

    if high[2] < level and high < level and (high[1] > level):
        label.new(bar_index - 1, high[1], string.tostring(vol_sum if lbl_data else high[1], format.volume if lbl_data else '#,####.###') + '\n⬙', color=NA(Color), textcolor=color.red, style=label.style_label_down)

    if low[2] > level and low[1] < level and (low > level):
        label.new(bar_index - 1, low[1], '⬘\n' + string.tostring(vol_sum if lbl_data else low[1], format.volume if lbl_data else '#,####.###'), color=NA(Color), textcolor=color.lime, style=label.style_label_up)

    barcolor(shift_col, title='Bar Color')
    plotcandle(open, high, low, close, title='Candles Color', color=shift_col, wickcolor=shift_col, bordercolor=shift_col, force_overlay=True)

    plot(strategy.position_avg_price if strategy.position_size != 0 else na, 'Entry Price', color=color.white, linewidth=1, style=plot.style_linebr)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)