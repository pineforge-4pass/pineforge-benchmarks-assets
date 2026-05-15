"""
@pyne

This code was compiled by PyneComp v6.0.31 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import currency, hour, minute, script, strategy


@script.strategy("PF probe 67 - same id exit replace", shorttitle="PF_P67_EXITREPL", overlay=True, initial_capital=1000000, currency=currency.USD, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1, pyramiding=1, process_orders_on_close=False)
def main():
    if hour == 8 and minute == 15 and (strategy.position_size == 0):
        strategy.entry('L', strategy.long, qty=1, comment='long for exit replace')
    if strategy.position_size > 0:
        entry = strategy.position_avg_price
        strategy.exit('X', 'L', limit=entry * 1.01, stop=entry * 0.99, comment='first exit')
        strategy.exit('X', 'L', limit=entry * 1.003, stop=entry * 0.997, comment='replacement exit')

    if strategy.position_size > 0 and hour == 16 and (minute == 15):
        strategy.close('L', comment='timeout')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
