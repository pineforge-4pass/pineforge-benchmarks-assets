"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from enum import StrEnum as Enum
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    bar_index, barstate, close, color, high, input, location, low, map, na,
    nz, open, plot, plotchar, script, size, strategy, ta
)
from pynecore.types import Persistent


class Aggression(Enum):
    conservative = 'Conservative'
    balanced = 'Balanced'
    aggressive = 'Aggressive'


@udt
class LayerInputs:
    rsi_len: int = 14
    ma_len: int = 20
    bb_len: int = 20
    bb_mult: float = 2.0


@udt
class RsiLayer:
    value: float = na(float)
    contrib: int = 0


@udt
class TrendLayer:
    ema: float = na(float)
    contrib: int = 0


@udt
class BbLayer:
    mid: float = na(float)
    upper: float = na(float)
    lower: float = na(float)
    contrib: int = 0


@udt
class ScoreSnapshot:
    rsi_c: int = 0
    trend_c: int = 0
    bb_c: int = 0


@udt
class VolContext:
    atr: float = na(float)
    atr_ma: float = na(float)
    ratio: float = 1.0


@udt
class OhlcBar:
    o: float = na(float)
    h: float = na(float)
    l: float = na(float)
    c: float = na(float)


@udt
class SessionScratch:
    in_session: bool = True
    bar_streak: int = 0


@udt
class GateState:
    vol_ok: bool = True
    map_ok: bool = True


@script.strategy("UDT Regime Stack (PF stress)", overlay=True, initial_capital=1000000, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    rsiLen=input.int(14, "RSI Length", minval=1),
    maLen=input.int(20, "MA Length", minval=1),
    bbLen=input.int(20, "BB Length", minval=5),
    bbMult=input.float(2.0, "BB Mult", step=0.1),
    profile=input.enum(Aggression.balanced, "Stress profile")
):

    cfg: Persistent[LayerInputs] = LayerInputs(rsiLen, maLen, bbLen, bbMult)

    thr_long: Persistent[float] = 2.0
    thr_short: Persistent[float] = -2.0
    gateMap: Persistent[dict[str, float]] = map.new()
    if barstate.isfirst:
        map.put(gateMap, 'long', 2.0)
        map.put(gateMap, 'short', -2.0)
        map.put(gateMap, 'exit_long', 0.0)
        map.put(gateMap, 'exit_short', 0.0)

    __switch__ = profile
    if __switch__ == Aggression.conservative:
        thr_long = nz(map.get(gateMap, 'long'), 2.0)
        thr_short = nz(map.get(gateMap, 'short'), -2.0)
    elif __switch__ == Aggression.balanced:
        thr_long = nz(map.get(gateMap, 'long'), 2.0)
        thr_short = nz(map.get(gateMap, 'short'), -2.0)
    elif __switch__ == Aggression.aggressive:
        thr_long = nz(map.get(gateMap, 'long'), 2.0)
        thr_short = nz(map.get(gateMap, 'short'), -2.0)
    else:
        thr_long = nz(map.get(gateMap, 'long'), 2.0)
        thr_short = nz(map.get(gateMap, 'short'), -2.0)

    rsiVal = ta.rsi(close, rsiLen)
    emaVal = ta.ema(close, maLen)
    bbMid, bbUpper, bbLower = ta.bb(close, bbLen, bbMult)
    atrVal = ta.atr(14)
    atrMa = ta.sma(atrVal, 20)
    atrRatio = atrVal / atrMa if atrMa > 0 else 1.0

    cfg.rsi_len = rsiLen
    cfg.ma_len = maLen
    cfg.bb_len = bbLen
    cfg.bb_mult = bbMult

    rsiL: Persistent[RsiLayer] = RsiLayer(na, 0)
    trL: Persistent[TrendLayer] = TrendLayer(na, 0)
    bbL: Persistent[BbLayer] = BbLayer(na, na, na, 0)
    snap: Persistent[ScoreSnapshot] = ScoreSnapshot(0, 0, 0)
    vol: Persistent[VolContext] = VolContext(na, na, 1.0)
    curBar: Persistent[OhlcBar] = OhlcBar(na, na, na, na)
    sess: Persistent[SessionScratch] = SessionScratch(True, 0)
    gates: Persistent[GateState] = GateState(True, True)

    rsiL.value = rsiVal
    rsiL.contrib = 1 if rsiVal > 50 else -1 if rsiVal < 50 else 0
    trL.ema = emaVal
    trL.contrib = 1 if close > emaVal else -1
    bbL.mid = bbMid
    bbL.upper = bbUpper
    bbL.lower = bbLower
    bbL.contrib = 1 if close > bbMid else -1
    vol.atr = atrVal
    vol.atr_ma = atrMa
    vol.ratio = atrRatio
    curBar.o = open
    curBar.h = high
    curBar.l = low
    curBar.c = close

    gates.vol_ok = vol.ratio < 25.0
    gates.map_ok = map.contains(gateMap, 'long') and map.contains(gateMap, 'short')

    score = rsiL.contrib + trL.contrib + bbL.contrib
    snap.rsi_c = rsiL.contrib
    snap.trend_c = trL.contrib
    snap.bb_c = bbL.contrib

    sess.in_session = True

    sess.bar_streak = sess.bar_streak + 1 if bar_index > 0 and close == close[1] else 0

    prevScore: Persistent[int] = na(int)
    longCond = gates.vol_ok and gates.map_ok and (score >= thr_long) and (not na(prevScore)) and (prevScore < thr_long)
    shortCond = gates.vol_ok and gates.map_ok and (score <= thr_short) and (not na(prevScore)) and (prevScore > thr_short)

    if longCond:
        strategy.entry('Long', strategy.long)
    if shortCond:
        strategy.entry('Short', strategy.short)

    exitL = nz(map.get(gateMap, 'exit_long'), 0.0)
    exitS = nz(map.get(gateMap, 'exit_short'), 0.0)
    if strategy.position_size > 0 and score <= exitL:
        strategy.close('Long')
    if strategy.position_size < 0 and score >= exitS:
        strategy.close('Short')

    prevScore = score

    plot(emaVal, 'EMA', color=color.blue)
    plot(bbUpper, 'BB Upper', color=color.gray)
    plot(bbLower, 'BB Lower', color=color.gray)

    plotchar(high if ta.crossover(score, thr_long) else na, 'Long cross', '▲', location=location.abovebar, color=color.teal, size=size.tiny)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
