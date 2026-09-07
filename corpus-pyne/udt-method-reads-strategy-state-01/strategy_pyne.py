"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method
from pynecore.core.pine_udt import udt
from pynecore.lib import bar_index, close, script, strategy, ta
from pynecore.types import Persistent


@udt
class Risk:
    cooldown_bars: int = 5
    last_exit_bar: int = -1000
    max_drawdown_pct: float = 0.05


@script.strategy("PF UDT probe 13 - strategy state in method", shorttitle="UDT_p13_STR", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    @method
    def allowsEntry(self: Risk):
        flatOk: bool = strategy.position_size == 0
        cooldownOk: bool = bar_index - self.last_exit_bar >= self.cooldown_bars
        ddLimit: float = strategy.initial_capital * self.max_drawdown_pct
        ddOk: bool = strategy.netprofit >= -ddLimit
        equityOk: bool = strategy.equity > 0.0
        return flatOk and cooldownOk and ddOk and equityOk

    risk: Persistent[Risk] = Risk(5, -1000, 0.05)

    emaFast = ta.ema(close, 9)
    emaSlow = ta.ema(close, 21)

    if ta.crossover(emaFast, emaSlow) and allowsEntry(risk):
        strategy.entry('L', strategy.long, qty=1, comment='entry long')
    if ta.crossunder(emaFast, emaSlow) and strategy.position_size > 0:
        strategy.close('L', comment='exit long')
        risk.last_exit_bar = bar_index


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
