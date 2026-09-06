"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import input, na, script, strategy, time, timeframe
from pynecore.types import Series


@script.strategy("VCP probe 07 - session ny", shorttitle="VCP_p07", overlay=True, initial_capital=1000000, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main(
    i_session=input.session("0800-1600", "Active Trading Session"),
    i_tz=input.string("America/New_York", "Timezone", options=("America/New_York", "Europe/London", "Asia/Tokyo", "UTC"))
):

    inSession: Series[bool] = not na(time(timeframe.period, i_session, i_tz))

    sessionStart: bool = inSession and (not inSession[1])
    sessionEnd: bool = not inSession and inSession[1]

    if sessionStart and strategy.position_size == 0:
        strategy.entry('L', strategy.long, qty=1, comment='ny session open')

    if sessionEnd and strategy.position_size > 0:
        strategy.close('L', comment='ny session close exit')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
