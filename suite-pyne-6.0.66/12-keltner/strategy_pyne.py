"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, currency, display, high, input, low, nz, script, strategy,
    syminfo, ta
)
from pynecore.types import Series


@script.strategy(title="Keltner Channels Strategy", overlay=True, use_bar_magnifier=False, initial_capital=1000000, currency=currency.USD, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    length=input.int(20, minval=1),
    mult=input.float(2.0, "Multiplier"),
    src: Series[float] = input(close, title="Source"),
    exp=input(True, "Use Exponential MA", display=display.none),
    BandsStyle=input.string("Average True Range", options=("Average True Range", "True Range", "Range"), title="Bands Style", display=display.none),
    atrlength=input(10, "ATR Length", display=display.none)
):
    def esma(source, length):
        s = ta.sma(source, length)
        e = ta.ema(source, length)
        return e if exp else s

    ma = esma(src, length)
    rangema = ta.tr(True) if BandsStyle == 'True Range' else ta.atr(atrlength) if BandsStyle == 'Average True Range' else ta.rma(high - low, length)
    upper = ma + rangema * mult
    lower = ma - rangema * mult
    crossUpper = ta.crossover(src, upper)
    crossLower = ta.crossunder(src, lower)
    bprice: Series[float] = 0.0
    bprice = high + syminfo.mintick if crossUpper else nz(bprice[1])
    sprice: Series[float] = 0.0
    sprice = low - syminfo.mintick if crossLower else nz(sprice[1])
    crossBcond: Series[bool] = False
    crossBcond = True if crossUpper else crossBcond[1]
    crossScond: Series[bool] = False
    crossScond = True if crossLower else crossScond[1]
    cancelBcond = crossBcond and (src < ma or high >= bprice)
    cancelScond = crossScond and (src > ma or low <= sprice)
    if cancelBcond:
        strategy.cancel('KltChLE')
    if crossUpper:
        strategy.entry('KltChLE', strategy.long, stop=bprice, comment='KltChLE')
    if cancelScond:
        strategy.cancel('KltChSE')
    if crossLower:
        strategy.entry('KltChSE', strategy.short, stop=sprice, comment='KltChSE')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
