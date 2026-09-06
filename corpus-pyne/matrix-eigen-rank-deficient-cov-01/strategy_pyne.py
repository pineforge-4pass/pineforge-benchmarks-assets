"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import array, bar_index, close, matrix, na, nz, script, strategy, ta
from pynecore.types import Matrix, Persistent


@script.strategy("PF typed-matrix probe 02 - eigen rank deficient", shorttitle="TM_p02_EIG", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    N: int = 32
    def mean(src, len):
        return ta.sma(src, len)

    c1: float = close
    c2: float = close * 2.0
    c3: float = close * 3.0

    m1: float = mean(c1, N)
    m2: float = mean(c2, N)
    m3: float = mean(c3, N)

    cov3: Persistent[Matrix[float]] = matrix.new(3, 3, 0.0)

    d1: float = nz(c1 - m1, 0.0)
    d2: float = nz(c2 - m2, 0.0)
    d3: float = nz(c3 - m3, 0.0)

    matrix.set(cov3, 0, 0, d1 * d1)
    matrix.set(cov3, 0, 1, d1 * d2)
    matrix.set(cov3, 0, 2, d1 * d3)
    matrix.set(cov3, 1, 0, d2 * d1)
    matrix.set(cov3, 1, 1, d2 * d2)
    matrix.set(cov3, 1, 2, d2 * d3)
    matrix.set(cov3, 2, 0, d3 * d1)
    matrix.set(cov3, 2, 1, d3 * d2)
    matrix.set(cov3, 2, 2, d3 * d3)

    warmedUp: bool = bar_index >= N
    evals: list[float] = matrix.eigenvalues(cov3) if warmedUp else array.new_float(0)
    emin: float = array.min(evals) if array.size(evals) > 0 else na
    eigenOk: bool = not na(emin) and emin > 1e-09

    emaFast = ta.ema(close, 9)
    emaSlow = ta.ema(close, 21)

    baseEntry: bool = ta.crossover(emaFast, emaSlow)
    baseExit: bool = ta.crossunder(emaFast, emaSlow)

    if baseEntry and strategy.position_size == 0:
        if eigenOk:
            strategy.entry('L_eig', strategy.long, qty=1, comment='entry long eig-ok')
        else:
            strategy.entry('L_fb', strategy.long, qty=1, comment='entry long fallback')
    if baseExit and strategy.position_size > 0:
        strategy.close_all(comment='exit')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
