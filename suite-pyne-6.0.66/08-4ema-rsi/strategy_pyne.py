"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alert, bgcolor, close, color, currency, input, na, plot, script,
    strategy, ta
)


@script.strategy("4-EMA & RSI Trend Pullback [Binary Options_20260320]", shorttitle="4EMA+RSI", overlay=True, use_bar_magnifier=False, initial_capital=1000000, currency=currency.USD, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    len7=input.int(7, title="EMA 7 (Fast Trigger)", group="EMA Settings"),
    len21=input.int(21, title="EMA 21 (Slow Trigger)", group="EMA Settings"),
    len50=input.int(50, title="EMA 50 (Trend & Dynamic Stop)", group="EMA Settings"),
    len200=input.int(200, title="EMA 200 (Macro Trend)", group="EMA Settings"),
    rsi_len=input.int(14, title="RSI Length", group="RSI Settings"),
    rsi_ob=input.int(70, title="RSI Overbought (Max for Longs)", group="RSI Settings"),
    rsi_os=input.int(30, title="RSI Oversold (Min for Shorts)", group="RSI Settings"),
    rsi_mid=input.int(50, title="RSI Centerline (Momentum Shift)", group="RSI Settings")
):

    ema7 = ta.ema(close, len7)
    ema21 = ta.ema(close, len21)
    ema50 = ta.ema(close, len50)
    ema200 = ta.ema(close, len200)

    rsi_val = ta.rsi(close, rsi_len)

    plot(ema7, color=color.new(color.blue, 0), title='EMA 7', linewidth=1)
    plot(ema21, color=color.new(color.orange, 0), title='EMA 21', linewidth=2)
    plot(ema50, color=color.new(color.green, 0), title='EMA 50', linewidth=2)
    plot(ema200, color=color.new(color.red, 0), title='EMA 200', linewidth=3)

    bullish_macro = ema50 > ema200
    bearish_macro = ema50 < ema200

    rsi_long_ok = rsi_val > rsi_mid and rsi_val < rsi_ob

    rsi_short_ok = rsi_val < rsi_mid and rsi_val > rsi_os

    long_trigger = ta.crossover(ema7, ema21) and rsi_long_ok
    short_trigger = ta.crossunder(ema7, ema21) and rsi_short_ok

    long_exit = ta.crossunder(ema7, ema21) or close < ema50
    short_exit = ta.crossover(ema7, ema21) or close > ema50

    if bullish_macro and long_trigger:
        strategy.entry('Long', strategy.long, comment='Buy')
        alert('🟢 [LONG ENTRY] 7/21 EMA Cross UP + RSI Confirmed. Trend Bullish.', alert.freq_once_per_bar_close)

    if strategy.position_size > 0 and long_exit:
        strategy.close('Long', comment='Exit Long')
        alert('🔴 [LONG EXIT] Momentum shifted down or 50 EMA broken.', alert.freq_once_per_bar_close)

    if bearish_macro and short_trigger:
        strategy.entry('Short', strategy.short, comment='Sell')
        alert('🔴 [SHORT ENTRY] 7/21 EMA Cross DOWN + RSI Confirmed. Trend Bearish.', alert.freq_once_per_bar_close)

    if strategy.position_size < 0 and short_exit:
        strategy.close('Short', comment='Exit Short')
        alert('🟢 [SHORT EXIT] Momentum shifted up or 50 EMA broken.', alert.freq_once_per_bar_close)

    perfect_bull = ema7 > ema21 and ema21 > ema50 and (ema50 > ema200)
    perfect_bear = ema7 < ema21 and ema21 < ema50 and (ema50 < ema200)
    bgcolor(color.new(color.green, 90) if perfect_bull else color.new(color.red, 90) if perfect_bear else na)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
