"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    array, close, currency, high, input, low, matrix, na, open, script,
    strategy, ta
)
from pynecore.types import Matrix, Persistent


@script.strategy("Matrix Eigen PCA", overlay=False, initial_capital=1000000, currency=currency.USD, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    length=input.int(14, "Length", minval=2)
):
    v1 = close - open
    v2 = high - low

    v1_mean = ta.sma(v1, length)
    v2_mean = ta.sma(v2, length)

    cov11 = ta.sma((v1 - v1_mean) * (v1 - v1_mean), length)
    cov12 = ta.sma((v1 - v1_mean) * (v2 - v2_mean), length)
    cov21 = cov12
    cov22 = ta.sma((v2 - v2_mean) * (v2 - v2_mean), length)

    m: Persistent[Matrix[float]] = matrix.new(2, 2, 0.0)
    matrix.set(m, 0, 0, cov11)
    matrix.set(m, 0, 1, cov12)
    matrix.set(m, 1, 0, cov21)
    matrix.set(m, 1, 1, cov22)

    covReady = not na(cov11) and (not na(cov12)) and (not na(cov22))

    lam: float = na(float)
    if covReady:
        lam = array.get(matrix.eigenvalues(m), 0) if array.size(matrix.eigenvalues(m)) > 0 else na

    lamSma = ta.sma(lam, length)

    if covReady and (not na(lam)) and (not na(lamSma)) and ta.crossover(lam, lamSma):
        strategy.entry('Long', strategy.long)
    if covReady and (not na(lam)) and (not na(lamSma)) and ta.crossunder(lam, lamSma):
        strategy.entry('Short', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
