"""
@pyne edge

This code was compiled by PyneComp v6.0.66 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alert, array, bar_index, barcolor, barstate, close, color, currency,
    display, fill, high, hl2, input, low, math, na, plot, position, script, size, strategy, string,
    ta, table
)
from pynecore.types import Persistent, Table


@script.strategy("BOS Waves Curved - Strategy", overlay=True, use_bar_magnifier=False, initial_capital=1000000, currency=currency.USD, process_orders_on_close=False, pyramiding=1, commission_type=strategy.commission.percent, commission_value=0, slippage=0, default_qty_type=strategy.fixed, default_qty_value=1)
def main(
    atrLength=input.int(14, "ATR Length", minval=1, group="Supertrend Settings", tooltip="Number of bars for ATR calculation. Higher = smoother, Lower = more responsive."),
    atrMult=input.float(2.0, "ATR Multiplier", minval=0.1, group="Supertrend Settings", tooltip="Distance of bands from price. Higher = wider bands, fewer signals."),
    radiusStrength=input.float(0.002, "Radius Strength", minval=0.001, maxval=0.3, step=0.001, group="Curve Settings", tooltip='Controls curve acceleration strength.\n\n' + 'Lower = Tighter curves (responsive)\n' + 'Higher = Wider curves (smoother)'),
    smoothness=input.int(5, "Smoothness", minval=1, maxval=20, group="Curve Settings", tooltip="Smoothing applied to curved band. Higher = smoother curves, less noise."),
    upColor=input.color(color.green, "Up Trend", group="Color Settings", tooltip="Color for uptrend band and signals."),
    dnColor=input.color(color.red, "Down Trend", group="Color Settings", tooltip="Color for downtrend band and signals."),
    showTable=input.bool(False, title="顯示智能提示"),
    tp_alert_enabled=input.bool(False, title="啟用盈利通知", group="客製化通知"),
    tp_alert=input.int(0, title="盈利通知間距", group="客製化通知"),
    tp_enabled=input.bool(False, title="啟用自動停利出場", group="客製化出場"),
    tp_distance=input.int(100, title="自動停利價格", group="客製化出場"),
    sl_enabled=input.bool(False, title="啟用自動停損出場", group="客製化出場"),
    sl_distance=input.int(100, title="自動停損價格", group="客製化出場"),
    tpsl_percentage=input.int(50, minval=0, maxval=100, title="自動停利停損百分比(%)")
):




    atr = ta.atr(atrLength)
    src = hl2

    upperBand = src + atrMult * atr
    lowerBand = src - atrMult * atr

    supertrend: Persistent[float] = na(float)
    direction: Persistent[int] = 1

    if na(supertrend):
        supertrend = lowerBand
        direction = 1

    prevSupertrend: float = supertrend

    if direction == 1:
        supertrend = upperBand if close < prevSupertrend else math.max(lowerBand, prevSupertrend)
    else:
        supertrend = lowerBand if close > prevSupertrend else math.min(upperBand, prevSupertrend)

    prevDirection: int = direction
    if close < supertrend:
        direction = -1
    if close > supertrend:
        direction = 1

    entryPrice: Persistent[float] = na(float)
    exitPrice: Persistent[float] = na(float)
    positionActive: Persistent[bool] = False
    currentDirection: Persistent[int] = 0

    profitHistory: Persistent[list[float]] = array.new_float(0)

    pivotLevels: Persistent[list[float]] = array.new_float(0)
    pivotBars: Persistent[list[int]] = array.new_int(0)
    lastPivotHigh: Persistent[float] = na(float)
    lastPivotLow: Persistent[float] = na(float)
    pivotLength: Persistent[int] = 5

    pivotHigh = ta.pivothigh(high, pivotLength, pivotLength)
    pivotLow = ta.pivotlow(low, pivotLength, pivotLength)

    if not na(pivotHigh):
        array.unshift(pivotLevels, pivotHigh)
        array.unshift(pivotBars, bar_index - pivotLength)
        lastPivotHigh = pivotHigh
        if array.size(pivotLevels) > 10:
            array.pop(pivotLevels)
            array.pop(pivotBars)

    if not na(pivotLow):
        array.unshift(pivotLevels, pivotLow)
        array.unshift(pivotBars, bar_index - pivotLength)
        lastPivotLow = pivotLow
        if array.size(pivotLevels) > 10:
            array.pop(pivotLevels)
            array.pop(pivotBars)

    keyResistance: Persistent[float] = na(float)
    keySupport: Persistent[float] = na(float)
    nearbyResistance: Persistent[float] = na(float)
    nearbySupport: Persistent[float] = na(float)

    if not na(lastPivotHigh) and (not na(lastPivotLow)):
        if direction == 1:
            keySupport = lastPivotLow
            keyResistance = lastPivotHigh
        else:
            keyResistance = lastPivotHigh
            keySupport = lastPivotLow

    recentHigh: Persistent[float] = na(float)
    recentLow: Persistent[float] = na(float)
    lookback: int = 20

    recentHigh = ta.highest(high, lookback)
    recentLow = ta.lowest(low, lookback)

    priceRange = ta.atr(14) * 3
    currentPrice = close

    if not na(recentHigh) and recentHigh > currentPrice and (recentHigh - currentPrice < priceRange * 2):
        nearbyResistance = recentHigh

    if not na(recentLow) and recentLow < currentPrice and (currentPrice - recentLow < priceRange * 2):
        nearbySupport = recentLow

    finalResistance = nearbyResistance if not na(nearbyResistance) else keyResistance
    finalSupport = nearbySupport if not na(nearbySupport) else keySupport

    breakoutSignal: bool = False
    breakdownSignal: bool = False
    approachingResistance: bool = False
    approachingSupport: bool = False

    if not na(finalResistance) and close > finalResistance and (close[1] <= finalResistance):
        breakoutSignal = True

    if not na(finalSupport) and close < finalSupport and (close[1] >= finalSupport):
        breakdownSignal = True

    warningDistance = ta.atr(14) * 0.5

    if not na(finalResistance) and close < finalResistance:
        distanceToResistance = finalResistance - close
        if distanceToResistance <= warningDistance and distanceToResistance > 0:
            approachingResistance = True

    if not na(finalSupport) and close > finalSupport:
        distanceToSupport = close - finalSupport
        if distanceToSupport <= warningDistance and distanceToSupport > 0:
            approachingSupport = True

    anchorPrice: Persistent[float] = na(float)
    anchorBar: Persistent[int] = na(int)
    velocity: Persistent[float] = 0.0
    barCount: Persistent[int] = 0

    trendChanged: bool = direction != prevDirection

    if trendChanged:
        anchorPrice = supertrend
        anchorBar = bar_index
        velocity = 0.0
        barCount = 0

        if positionActive and (not na(entryPrice)):
            profit: Persistent[float] = na(float)
            if currentDirection == 1:
                profit = close[1] - entryPrice
            elif currentDirection == -1:
                profit = entryPrice - close[1]

            if not na(profit):
                array.unshift(profitHistory, profit)
                if array.size(profitHistory) > 5:
                    array.pop(profitHistory)

            positionActive = False
            exitPrice = close[1]

        if direction == 1 or direction == -1:
            entryPrice = close
            positionActive = True
            currentDirection = direction
            exitPrice = na

    barCount = barCount + 1

    if not na(anchorPrice):
        velocity = velocity + radiusStrength * barCount

        if direction == 1:
            supertrend = anchorPrice + velocity
        else:
            supertrend = anchorPrice - velocity

    curvedBand = ta.sma(supertrend, smoothness)

    trendColor = upColor if direction == 1 else dnColor

    plot(curvedBand, 'Curved Radius Band', color=trendColor, linewidth=3)

    basePlot = plot(close, display=display.none)
    bandPlot = plot(curvedBand, display=display.none)
    fill(basePlot, bandPlot, color.new(trendColor, 85))

    outerBand = curvedBand + atr if direction == 1 else curvedBand - atr
    plot(outerBand, 'Outer Band', color=color.new(trendColor, 70), linewidth=1, style=plot.style_circles)

    barcolor(upColor if direction == 1 else dnColor, title='Trend Candle Color')

    infoTable: Persistent[Table] = table.new(position.middle_right, 2, 8, bgcolor=color.new(color.gray, 70), border_width=2)
    alertTable: Persistent[Table] = table.new(position.bottom_right, 1, 1, bgcolor=color.new(color.red, 75), border_width=2)
    reminderWindow: Persistent[Table] = table.new(position.top_right, 1, 6, bgcolor=color.new(color.purple, 70), border_width=2)

    if (barstate.islast or barstate.isconfirmed) and showTable:
        trendStatusText = '多空 ●' if direction == 1 else '多空 ●' if direction == -1 else '無趨勢'
        trendStatusColor = color.green if direction == 1 else color.red if direction == -1 else color.gray

        atrChange = ta.change(atr, 5)
        convergenceText = '正常 ■' if atrChange < 0 else '擴散'
        convergenceColor = color.green if atrChange < 0 else color.orange

        priceDistance = math.abs(close - curvedBand)
        avgDistance = ta.sma(priceDistance, 20)
        divergenceText = '發散' if priceDistance > avgDistance * 1.5 else '收斂'
        divergenceColor = color.red if priceDistance > avgDistance * 1.5 else color.gray

        riskText: str = "注意 ▲"
        riskColor = color.orange
        if positionActive and (not na(entryPrice)):
            currentProfit: Persistent[float] = na(float)
            if currentDirection == 1:
                currentProfit = close - entryPrice
            elif currentDirection == -1:
                currentProfit = entryPrice - close
            if not na(currentProfit) and currentProfit < -50:
                riskText = "高風險 ▲"
                riskColor = color.red
            elif not na(currentProfit) and currentProfit > 0:
                riskText = "良好 ●"
                riskColor = color.green

        suggestionText = '良好時機 ✓' if direction != 0 else '等待信號'
        suggestionColor = color.green if direction != 0 else color.gray

        historySize = array.size(profitHistory)
        learningText: str = "無標示"
        learningColor = color.gray
        if historySize >= 3:
            recentProfit: float = 0.0
            for i in pine_range(0, 2):
                if i < historySize:
                    recentProfit += array.get(profitHistory, i)
            if recentProfit > 0:
                learningText = "表現良好"
                learningColor = color.green
            else:
                learningText = "需要調整"
                learningColor = color.orange

        table.cell(infoTable, 0, 0, '趨勢', text_color=color.white, bgcolor=color.new(color.gray, 80))
        table.cell(infoTable, 1, 0, trendStatusText, text_color=trendStatusColor, bgcolor=color.new(color.gray, 80))

        table.cell(infoTable, 0, 1, '收斂', text_color=color.white, bgcolor=color.new(color.gray, 80))
        table.cell(infoTable, 1, 1, convergenceText, text_color=convergenceColor, bgcolor=color.new(color.gray, 80))

        table.cell(infoTable, 0, 2, '發散', text_color=color.white, bgcolor=color.new(color.gray, 80))
        table.cell(infoTable, 1, 2, divergenceText, text_color=divergenceColor, bgcolor=color.new(color.gray, 80))

        table.cell(infoTable, 0, 3, '風險', text_color=color.white, bgcolor=color.new(color.gray, 80))
        table.cell(infoTable, 1, 3, riskText, text_color=riskColor, bgcolor=color.new(color.gray, 80))

        table.cell(infoTable, 0, 4, '建議', text_color=color.white, bgcolor=color.new(color.gray, 80))
        table.cell(infoTable, 1, 4, suggestionText, text_color=suggestionColor, bgcolor=color.new(color.gray, 80))

        table.cell(infoTable, 0, 5, '學習點', text_color=color.white, bgcolor=color.new(color.gray, 80))
        table.cell(infoTable, 1, 5, learningText, text_color=learningColor, bgcolor=color.new(color.gray, 80))

        if positionActive and (not na(entryPrice)):
            currentProfit: Persistent[float] = na(float)
            if currentDirection == 1:
                currentProfit = close - entryPrice
            elif currentDirection == -1:
                currentProfit = entryPrice - close

            table.cell(infoTable, 0, 6, '進場價', text_color=color.white, bgcolor=color.new(color.gray, 80))
            table.cell(infoTable, 1, 6, string.tostring(entryPrice, '#.##'), text_color=color.yellow, bgcolor=color.new(color.gray, 80))

            currentProfitText = ('+' + string.tostring(currentProfit, '#.##') if currentProfit > 0 else string.tostring(currentProfit, '#.##')) if not na(currentProfit) else '-'
            currentProfitColor = (color.green if currentProfit > 0 else color.red if currentProfit < 0 else color.gray) if not na(currentProfit) else color.gray
            table.cell(infoTable, 0, 7, '當前點數', text_color=color.white, bgcolor=color.new(color.gray, 80))
            table.cell(infoTable, 1, 7, currentProfitText, text_color=currentProfitColor, bgcolor=color.new(color.gray, 80))

        if trendChanged and positionActive:
            table.cell(alertTable, 0, 0, '⚠ 發現異常 平倉下單\n依據指導方向\n黃金反方向', text_color=color.white, bgcolor=color.new(color.red, 80), text_size=size.normal)

        reminderTitle: str = "💡 智能交易提醒"
        table.cell(reminderWindow, 0, 0, reminderTitle, text_color=color.white, bgcolor=color.new(color.fuchsia, 70), text_size=size.large)

        marketStatus: str = ""
        if direction == 1:
            marketStatus = "📈 當前多頭趨勢\n建議關注支撐位"
        elif direction == -1:
            marketStatus = "📉 當前空頭趨勢\n建議關注阻力位"
        else:
            marketStatus = "⏸️ 趨勢不明確\n建議等待突破"
        table.cell(reminderWindow, 0, 1, marketStatus, text_color=color.white, bgcolor=color.new(color.purple, 75), text_size=size.normal)

        riskReminder: str = ""
        if positionActive and (not na(entryPrice)):
            currentProfit: Persistent[float] = na(float)
            if currentDirection == 1:
                currentProfit = close - entryPrice
            elif currentDirection == -1:
                currentProfit = entryPrice - close

            if not na(currentProfit):
                if currentProfit < -30:
                    riskReminder = "⚠️ 虧損擴大中\n考慮止損退場"
                elif currentProfit > 50:
                    riskReminder = "✅ 獲利中\n可考慮部分獲利"
                else:
                    riskReminder = "📊 持倉中\n密切觀察走勢"
        else:
            riskReminder = "💤 目前無持倉\n等待進場機會"

        table.cell(reminderWindow, 0, 2, riskReminder, text_color=color.white, bgcolor=color.new(color.purple, 75), text_size=size.normal)

        operationAdvice: str = ""
        volatility = ta.atr(14) / close * 100
        if volatility > 2.0:
            operationAdvice = "⚡ 市場波動大\n減少倉位操作"
        elif volatility < 0.5:
            operationAdvice = "😴 市場平靜\n可考慮區間操作"
        else:
            operationAdvice = "⚖️ 正常波動\n按計劃執行"

        table.cell(reminderWindow, 0, 3, operationAdvice, text_color=color.white, bgcolor=color.new(color.purple, 75), text_size=size.normal)

        currentProfitInfo: str = ""
        if positionActive and (not na(entryPrice)):
            currentProfit: Persistent[float] = na(float)
            if currentDirection == 1:
                currentProfit = close - entryPrice
            elif currentDirection == -1:
                currentProfit = entryPrice - close

            if not na(currentProfit):
                profitText = '+' + string.tostring(currentProfit, '#.##') if currentProfit > 0 else string.tostring(currentProfit, '#.##')
                currentProfitInfo = '💰 目前' + ('賺' if currentProfit >= 0 else '虧') + '：' + profitText + ' 點'
            else:
                currentProfitInfo = "💰 目前盈虧：計算中"
        else:
            currentProfitInfo = "💤 目前無持倉"

        table.cell(reminderWindow, 0, 4, currentProfitInfo, text_color=color.white, bgcolor=color.new(color.purple, 75), text_size=size.normal)

        pivotInfo: str = ""
        warningText: str = ""

        if approachingResistance and (not na(finalResistance)):
            warningText = '⚠️ 接近阻力 ' + string.tostring(finalResistance - close, '#.##')
        elif approachingSupport and (not na(finalSupport)):
            warningText = '⚠️ 接近支撑 ' + string.tostring(close - finalSupport, '#.##')

        if not na(finalResistance) and (not na(finalSupport)):
            baseInfo = '🎯 阻力: ' + string.tostring(finalResistance, '#.##') + '\n🛡️ 支撐: ' + string.tostring(finalSupport, '#.##')
            pivotInfo = baseInfo + '\n' + warningText if warningText != '' else baseInfo
        elif not na(finalResistance):
            baseInfo = '🎯 阻力: ' + string.tostring(finalResistance, '#.##') + '\n🛡️ 支撐: 待確認'
            pivotInfo = baseInfo + '\n' + warningText if warningText != '' else baseInfo
        elif not na(finalSupport):
            baseInfo = '🎯 阻力: 待確認\n🛡️ 支撐: ' + string.tostring(finalSupport, '#.##')
            pivotInfo = baseInfo + '\n' + warningText if warningText != '' else baseInfo
        else:
            pivotInfo = "🎯 阻力: 待確認\n🛡️ 支撐: 待確認"

        table.cell(reminderWindow, 0, 5, pivotInfo, text_color=color.white, bgcolor=color.new(color.purple, 75), text_size=size.normal)

    buySignal = trendChanged and direction == 1
    sellSignal = trendChanged and direction == -1

    last_alert_price: Persistent[float] = 0
    accumulated_profit: Persistent[float] = 0.0

    if buySignal and strategy.position_size <= 0:
        strategy.entry('Buy', strategy.long, alert_message='long_entry')
        last_alert_price = close
        accumulated_profit = 0.0
        if tp_enabled or sl_enabled:
            tp_price = close + tp_distance if tp_enabled else na
            sl_price = close - sl_distance if sl_enabled else na
            strategy.exit('Exit Long', 'Buy', limit=tp_price, stop=sl_price, alert_message='long_exit', qty_percent=tpsl_percentage)

    if sellSignal and strategy.position_size >= 0:
        strategy.entry('Sell', strategy.short, alert_message='short_entry')
        last_alert_price = close
        accumulated_profit = 0.0
        if tp_enabled or sl_enabled:
            tp_price = close - tp_distance if tp_enabled else na
            sl_price = close + sl_distance if sl_enabled else na
            strategy.exit('Exit Short', 'Sell', limit=tp_price, stop=sl_price, alert_message='short_exit', qty_percent=tpsl_percentage)

    if strategy.position_size == 0 and (not na(last_alert_price)):
        last_alert_price = na

    alert_now: bool = False
    current_increment: float = 0.0

    if strategy.position_size > 0 and tp_alert_enabled and (not na(last_alert_price)):
        if close - last_alert_price >= tp_alert:
            current_increment = close - last_alert_price
            accumulated_profit += current_increment
            alert_now = True
            last_alert_price = close

    if strategy.position_size < 0 and tp_alert_enabled and (not na(last_alert_price)):
        if last_alert_price - close >= tp_alert:
            current_increment = last_alert_price - close
            accumulated_profit += current_increment
            alert_now = True
            last_alert_price = close

    if alert_now:
        alert('本次盈利增加: $' + string.tostring(current_increment) + ' | 累積盈利: $' + string.tostring(accumulated_profit) + ' | 當前價格: ' + string.tostring(close))

    alertDistance: float = 30.0

    nearBuySignal: bool = False
    if not buySignal and direction == 1 and (math.abs(close - curvedBand) <= alertDistance):
        nearBuySignal = True

    nearSellSignal: bool = False
    if not sellSignal and direction == -1 and (math.abs(close - curvedBand) <= alertDistance):
        nearSellSignal = True


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
