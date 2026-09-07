"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barstate, close, color, currency, dayofmonth, fill, high, input,
    location, low, math, na, plot, plotshape, position, script, shape, size, strategy, string, ta,
    table, time, timestamp, volume
)
from pynecore.types import Persistent, Series, Table


@script.strategy('Sol 3m scalping', overlay=True, margin_long=0, margin_short=0, calc_on_every_tick=False, use_bar_magnifier=False, initial_capital=1000000, currency=currency.USD, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    capital=input.int(title='Capital ($)', defval=1000, step=100, minval=100, maxval=1000000, group="💰 Risk Management"),
    risk_per_trade=input.float(title='Risk per Trade (%)', defval=1.0, step=0.1, minval=0.1, maxval=5.0, group="💰 Risk Management"),
    riskReward=input.float(title='Risk:Reward Ratio', defval=2.0, step=0.1, minval=1.0, maxval=5.0, group="💰 Risk Management"),
    use_leverage=input.int(title='Leverage', defval=5, minval=1, maxval=50, step=1, group="💰 Risk Management"),
    max_daily_loss=input.float(title='Max Daily Loss (%)', defval=3.0, step=0.5, minval=1.0, maxval=10.0, group="💰 Risk Management"),
    max_positions=input.int(title='Max Open Positions', defval=5, minval=1, maxval=10, step=1, group="💰 Risk Management", tooltip="Maximum number of positions that can be open simultaneously"),
    sr_lookback=input.int(title='S/R Lookback Period', defval=20, minval=5, maxval=100, group="📊 Support & Resistance"),
    sr_tolerance=input.float(title='S/R Zone Width (%)', defval=0.3, step=0.1, minval=0.1, maxval=1.0, group="📊 Support & Resistance", tooltip="How close price must be to S/R level to trigger (as % of price)"),
    bb_length=input.int(title='BB Length', defval=20, minval=5, maxval=50, group="📈 Bollinger Bands"),
    bb_mult=input.float(title='BB Multiplier', defval=2.0, step=0.1, minval=1.0, maxval=4.0, group="📈 Bollinger Bands"),
    bb_src: Series[float] = input.source(title='BB Source', defval=close, group="📈 Bollinger Bands"),
    fast_ma_len=input.int(title='Fast MA Length', defval=9, minval=3, maxval=50, group="🔀 MA Cross"),
    slow_ma_len=input.int(title='Slow MA Length', defval=21, minval=10, maxval=100, group="🔀 MA Cross"),
    ma_type=input.string(title='MA Type', defval='EMA', options=('EMA', 'SMA', 'WMA'), group="🔀 MA Cross"),
    use_volume_filter=input.bool(title='Use Volume Filter', defval=True, group="🔧 Filters"),
    vol_mult=input.float(title='Min Volume Multiplier', defval=1.2, step=0.1, minval=0.5, maxval=3.0, group="🔧 Filters", tooltip="Volume must be this multiple of 20-bar average"),
    use_atr_filter=input.bool(title='Use ATR Volatility Filter', defval=True, group="🔧 Filters"),
    atr_min_mult=input.float(title='Min ATR Multiplier', defval=0.5, step=0.1, minval=0.1, maxval=2.0, group="🔧 Filters", tooltip="Current ATR must be at least this multiple of 50-bar ATR average"),
    min_bars_between=input.int(title='Min Bars Between Entries', defval=3, minval=1, maxval=20, group="🔧 Filters", tooltip="Minimum bars between opening new positions to avoid clustering"),
    testStartYear=input.int(2025, "Backtest Start Year", group="📅 Backtest Period"),
    testStartMonth=input.int(1, "Backtest Start Month", group="📅 Backtest Period"),
    testStartDay=input.int(1, "Backtest Start Day", group="📅 Backtest Period")
):



    testPeriodStart = timestamp(testStartYear, testStartMonth, testStartDay, 0, 0)
    def testPeriod():
        return time >= testPeriodStart

    pivot_high = ta.pivothigh(high, sr_lookback, sr_lookback)
    pivot_low = ta.pivotlow(low, sr_lookback, sr_lookback)

    resistance_level: Persistent[float] = na(float)
    support_level: Persistent[float] = na(float)

    if not na(pivot_high):
        resistance_level = pivot_high
    if not na(pivot_low):
        support_level = pivot_low

    sr_zone = close * (sr_tolerance / 100)
    near_resistance = not na(resistance_level) and math.abs(close - resistance_level) <= sr_zone
    near_support = not na(support_level) and math.abs(close - support_level) <= sr_zone

    bb_basis = ta.sma(bb_src, bb_length)
    bb_dev = bb_mult * ta.stdev(bb_src, bb_length)
    bb_upper = bb_basis + bb_dev
    bb_lower = bb_basis - bb_dev
    bb_pct = (close - bb_lower) / (bb_upper - bb_lower)

    bb_long_signal = close > bb_upper
    bb_short_signal = close < bb_lower

    def get_ma(src, length):
        __block_result__ = na
        __switch__ = ma_type
        if __switch__ == 'EMA':
            __block_result__ = ta.ema(src, length)
        elif __switch__ == 'SMA':
            __block_result__ = ta.sma(src, length)
        elif __switch__ == 'WMA':
            __block_result__ = ta.wma(src, length)
        return __block_result__

    fast_ma = get_ma(close, fast_ma_len)
    slow_ma = get_ma(close, slow_ma_len)

    ma_bearish_cross = ta.crossunder(fast_ma, slow_ma)
    ma_bullish_cross = ta.crossover(fast_ma, slow_ma)

    vol_avg = ta.sma(volume, 20)
    vol_ok = not use_volume_filter or volume >= vol_avg * vol_mult

    atr_val = ta.atr(14)
    atr_avg = ta.sma(atr_val, 50)
    atr_ok = not use_atr_filter or atr_val >= atr_avg * atr_min_mult

    long_score = (1 if near_resistance else 0) + (1 if bb_long_signal else 0) + (1 if ma_bearish_cross else 0)
    short_score = (1 if near_support else 0) + (1 if bb_short_signal else 0) + (1 if ma_bullish_cross else 0)

    reverse_long_condition = long_score >= 2 and vol_ok and atr_ok
    reverse_short_condition = short_score >= 2 and vol_ok and atr_ok

    trade_counter: Persistent[int] = 0
    daily_pnl: Persistent[float] = 0.0
    last_trade_day: Persistent[int] = 0
    bars_since_entry: Persistent[int] = 100

    bars_since_entry += 1

    current_day = dayofmonth
    if current_day != last_trade_day:
        daily_pnl = 0.0
        last_trade_day = current_day

    daily_loss_ok = daily_pnl > -(capital * max_daily_loss / 100)

    open_trades = strategy.opentrades

    can_open_new = open_trades < max_positions and bars_since_entry >= min_bars_between

    atr_stop_distance = atr_val * 1.5

    if testPeriod() and daily_loss_ok and can_open_new:
        if reverse_long_condition:
            trade_counter += 1
            entry_price = close
            stop_val = close - atr_stop_distance
            take_val = close + atr_stop_distance * riskReward

            risk_amount = capital * (risk_per_trade / 100)
            stop_dist_pct = math.abs(entry_price - stop_val) / entry_price
            qty_contracts = math.round(risk_amount / stop_dist_pct) / close if stop_dist_pct > 0 else 0.0

            trade_id = 'Long_' + string.tostring(trade_counter)

            if qty_contracts > 0:
                strategy.entry(trade_id, strategy.long, qty=qty_contracts)
                strategy.exit('Exit_' + string.tostring(trade_counter), from_entry=trade_id, limit=take_val, stop=stop_val)
                bars_since_entry = 0

        if reverse_short_condition:
            trade_counter += 1
            entry_price = close
            stop_val = close + atr_stop_distance
            take_val = close - atr_stop_distance * riskReward

            risk_amount = capital * (risk_per_trade / 100)
            stop_dist_pct = math.abs(stop_val - entry_price) / entry_price
            qty_contracts = math.round(risk_amount / stop_dist_pct) / close if stop_dist_pct > 0 else 0.0

            trade_id = 'Short_' + string.tostring(trade_counter)

            if qty_contracts > 0:
                strategy.entry(trade_id, strategy.short, qty=qty_contracts)
                strategy.exit('Exit_' + string.tostring(trade_counter), from_entry=trade_id, limit=take_val, stop=stop_val)
                bars_since_entry = 0

    if strategy.closedtrades > 0:
        last_pnl = strategy.closedtrades.profit(strategy.closedtrades - 1)
        if strategy.closedtrades != strategy.closedtrades[1]:
            daily_pnl += last_pnl

    plot(resistance_level, 'Resistance', color=color.new(color.red, 30), linewidth=2, style=plot.style_stepline_diamond)
    plot(support_level, 'Support', color=color.new(color.green, 30), linewidth=2, style=plot.style_stepline_diamond)

    p_bb_upper = plot(bb_upper, 'BB Upper', color=color.new(color.blue, 60))
    p_bb_lower = plot(bb_lower, 'BB Lower', color=color.new(color.blue, 60))
    p_bb_basis = plot(bb_basis, 'BB Basis', color=color.new(color.orange, 40))
    fill(p_bb_upper, p_bb_lower, color=color.new(color.blue, 92), title='BB Fill')

    plot(fast_ma, 'Fast MA', color=color.new(color.yellow, 20), linewidth=2)
    plot(slow_ma, 'Slow MA', color=color.new(color.purple, 20), linewidth=2)

    plotshape(reverse_long_condition and can_open_new and daily_loss_ok and testPeriod(), 'Reverse Long', shape.triangleup, location.belowbar, color.new(color.lime, 0), size=size.small)
    plotshape(reverse_short_condition and can_open_new and daily_loss_ok and testPeriod(), 'Reverse Short', shape.triangledown, location.abovebar, color.new(color.red, 0), size=size.small)

    dashboard: Persistent[Table] = table.new(position.top_right, 2, 9, bgcolor=color.new(color.black, 80), border_width=1)

    if barstate.islast:
        table.cell(dashboard, 0, 0, 'EFFORT 01', text_color=color.white, text_size=size.small, bgcolor=color.new(color.teal, 40))
        table.cell(dashboard, 1, 0, 'Dashboard', text_color=color.white, text_size=size.small, bgcolor=color.new(color.teal, 40))

        table.cell(dashboard, 0, 1, 'Open Trades', text_color=color.white, text_size=size.small)
        table.cell(dashboard, 1, 1, string.tostring(open_trades) + ' / ' + string.tostring(max_positions), text_color=color.orange if open_trades >= max_positions else color.lime, text_size=size.small)

        table.cell(dashboard, 0, 2, 'Net Position', text_color=color.white, text_size=size.small)
        pos_text = 'NET LONG' if strategy.position_size > 0 else 'NET SHORT' if strategy.position_size < 0 else 'FLAT'
        table.cell(dashboard, 1, 2, pos_text, text_color=color.lime if strategy.position_size > 0 else color.red if strategy.position_size < 0 else color.gray, text_size=size.small)

        table.cell(dashboard, 0, 3, 'Total Trades', text_color=color.white, text_size=size.small)
        table.cell(dashboard, 1, 3, string.tostring(trade_counter), text_color=color.white, text_size=size.small)

        table.cell(dashboard, 0, 4, 'Long Score', text_color=color.white, text_size=size.small)
        table.cell(dashboard, 1, 4, string.tostring(long_score) + '/3', text_color=color.lime, text_size=size.small)

        table.cell(dashboard, 0, 5, 'Short Score', text_color=color.white, text_size=size.small)
        table.cell(dashboard, 1, 5, string.tostring(short_score) + '/3', text_color=color.red, text_size=size.small)

        table.cell(dashboard, 0, 6, 'ATR', text_color=color.white, text_size=size.small)
        table.cell(dashboard, 1, 6, string.tostring(atr_val, '#.####'), text_color=color.orange, text_size=size.small)

        table.cell(dashboard, 0, 7, 'Daily P&L', text_color=color.white, text_size=size.small)
        table.cell(dashboard, 1, 7, string.tostring(daily_pnl, '#.##'), text_color=color.lime if daily_pnl >= 0 else color.red, text_size=size.small)

        table.cell(dashboard, 0, 8, 'Bars Since Entry', text_color=color.white, text_size=size.small)
        table.cell(dashboard, 1, 8, string.tostring(bars_since_entry), text_color=color.white, text_size=size.small)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
