import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    global tr_nb_fn, rma_nb_fn, sma_nb_fn, ema_nb_fn, rsi_nb_fn, logic_loop_fn
    close_p = df['close'].values
    open_p = df['open'].values
    high_p = df['high'].values
    low_p = df['low'].values
    n = len(df)

    # -------------------------------------------------------------------------
    # EMA helper
    # -------------------------------------------------------------------------
    @njit
    def ema_nb(arr, length):
        out = np.empty(len(arr))
        out[:] = np.nan
        # Find first non-nan index in arr
        first_idx = 0
        while first_idx < len(arr) and np.isnan(arr[first_idx]):
            first_idx += 1

        if len(arr) - first_idx < length:
            return out

        sma_init = 0.0
        for i in range(first_idx, first_idx + length):
            sma_init += arr[i]
        sma_init /= length
        out[first_idx + length - 1] = sma_init
        alpha = 2.0 / (length + 1)
        for i in range(first_idx + length, len(arr)):
            out[i] = alpha * arr[i] + (1 - alpha) * out[i-1]
        return out

    # -------------------------------------------------------------------------
    # RMA helper
    # -------------------------------------------------------------------------
    @njit
    def rma_nb(arr, length):
        out = np.empty(len(arr))
        out[:] = np.nan
        if len(arr) < length:
            return out
        # First rma is SMA
        sma_init = 0.0
        for i in range(length):
            sma_init += arr[i]
        sma_init /= length
        out[length-1] = sma_init
        alpha = 1.0 / length
        for i in range(length, len(arr)):
            out[i] = alpha * arr[i] + (1 - alpha) * out[i-1]
        return out

    # -------------------------------------------------------------------------
    # SMA helper
    # -------------------------------------------------------------------------
    @njit
    def sma_nb(arr, length):
        out = np.empty(len(arr))
        out[:] = np.nan
        # Find first non-nan index in arr
        first_idx = 0
        while first_idx < len(arr) and np.isnan(arr[first_idx]):
            first_idx += 1

        if len(arr) - first_idx < length:
            return out

        start_idx = first_idx + length - 1
        running_sum = 0.0
        for i in range(first_idx, first_idx + length):
            running_sum += arr[i]
        out[start_idx] = running_sum / length

        for i in range(first_idx + length, len(arr)):
            running_sum = running_sum - arr[i - length] + arr[i]
            out[i] = running_sum / length
        return out

    # -------------------------------------------------------------------------
    # TR (True Range) helper
    # -------------------------------------------------------------------------
    @njit
    def tr_nb(high, low, close):
        out = np.empty(len(close))
        out[0] = high[0] - low[0]
        for i in range(1, len(close)):
            out[i] = max(high[i] - low[i], abs(high[i] - close[i-1]), abs(low[i] - close[i-1]))
        return out

    # -------------------------------------------------------------------------
    # ATR helper
    # -------------------------------------------------------------------------
    @njit
    def atr_nb(high, low, close, length):
        tr = tr_nb(high, low, close)
        return rma_nb(tr, length)

    # -------------------------------------------------------------------------
    # RSI helper
    # -------------------------------------------------------------------------
    @njit
    def rsi_nb(close, length):
        out = np.empty(len(close))
        out[:] = np.nan
        if len(close) < length + 1:
            return out
        deltas = np.empty(len(close))
        deltas[0] = 0.0
        for i in range(1, len(close)):
            deltas[i] = close[i] - close[i-1]

        gains = np.where(deltas > 0, deltas, 0.0)
        losses = np.where(deltas < 0, -deltas, 0.0)

        avg_gains = rma_nb(gains, length)
        avg_losses = rma_nb(losses, length)

        for i in range(len(close)):
            if np.isnan(avg_gains[i]) or np.isnan(avg_losses[i]):
                continue
            if avg_losses[i] == 0:
                out[i] = 100.0
            else:
                rs = avg_gains[i] / avg_losses[i]
                out[i] = 100.0 - (100.0 / (1.0 + rs))
        return out

    # -------------------------------------------------------------------------
    # Pre-calculate Indicators
    # -------------------------------------------------------------------------
    i_adx_len = 14
    i_adx_trend = 25.0
    i_atr_len = 14
    i_vol_exp = 1.4
    i_vol_con = 0.6
    i_ma_fast = 21
    i_ma_slow = 55
    i_ma_trend = 200
    i_bias_thresh = 30.0
    i_rsi_len = 14
    i_rsi_bull = 55.0
    i_rsi_bear = 45.0
    i_macd_fast = 12
    i_macd_slow = 26
    i_macd_sig = 9
    i_press_len = 14
    i_press_smo = 5
    i_press_mom = 10
    i_press_thr = 0.05
    i_cooldown = 8

    # ADX chain pre-computations
    tr_v = tr_nb(high_p, low_p, close_p)
    p_dm = np.zeros(n)
    m_dm = np.zeros(n)
    for i in range(1, n):
        up = high_p[i] - high_p[i-1]
        down = low_p[i-1] - low_p[i]
        if up > down and up > 0:
            p_dm[i] = up
        elif down > up and down > 0:
            m_dm[i] = down
        else:
            p_dm[i] = 0.0
            m_dm[i] = 0.0
    s_tr = rma_nb(tr_v, i_adx_len)
    s_p = rma_nb(p_dm, i_adx_len)
    s_m = rma_nb(m_dm, i_adx_len)

    p_di_v = np.zeros(n)
    m_di_v = np.zeros(n)
    dx_v = np.zeros(n)
    for i in range(n):
        if s_tr[i] > 0:
            p_di_v[i] = 100 * s_p[i] / s_tr[i]
            m_di_v[i] = 100 * s_m[i] / s_tr[i]
        di_sum = p_di_v[i] + m_di_v[i]
        if di_sum > 0:
            dx_v[i] = 100 * abs(p_di_v[i] - m_di_v[i]) / di_sum

    adx_v = rma_nb(dx_v, i_adx_len)

    # ATR and vol_ratio
    atr_v = atr_nb(high_p, low_p, close_p, i_atr_len)
    atr_avg = sma_nb(atr_v, i_atr_len * 3)
    vol_ratio = np.ones(n)
    for i in range(n):
        if atr_avg[i] > 0:
            vol_ratio[i] = atr_v[i] / atr_avg[i]

    # Triple-EMA stack bias pre-computations
    ma_fast = ema_nb(close_p, i_ma_fast)
    ma_slow = ema_nb(close_p, i_ma_slow)
    ma_trend = ema_nb(close_p, i_ma_trend)

    # RSI
    rsi_v = rsi_nb(close_p, i_rsi_len)

    # MACD
    macd_line = ema_nb(close_p, i_macd_fast) - ema_nb(close_p, i_macd_slow)
    macd_sig = ema_nb(macd_line, i_macd_sig)
    macd_hist = macd_line - macd_sig

    # Pressure gauge
    bar_range = high_p - low_p
    raw_press = np.zeros(n)
    for i in range(n):
        raw_press[i] = (close_p[i] - low_p[i]) / bar_range[i] if bar_range[i] > 0 else 0.5
    press_r = ema_nb(raw_press, i_press_len)
    press_s = ema_nb(press_r, i_press_smo)

    # -------------------------------------------------------------------------
    # Core Logic Loop
    # -------------------------------------------------------------------------
    @njit
    def logic_loop(
        close_p, open_p, adx_v, p_di_v, m_di_v, vol_ratio,
        ma_fast, ma_slow, ma_trend, rsi_v, macd_hist, press_s
    ):
        entries = np.zeros(n, dtype=np.bool_)
        short_entries = np.zeros(n, dtype=np.bool_)
        exits = np.zeros(n, dtype=np.bool_)
        short_exits = np.zeros(n, dtype=np.bool_)

        bars_since_trade = 999
        pos = 0 # 1 for long, -1 for short, 0 for flat

        for i in range(1, n):
            # Evaluate all signals on historical bar i-1 (since order executes on bar i open)
            # Pine standard process_orders_on_close = False (execute on next bar's open)
            prev_idx = i - 1

            if np.isnan(adx_v[prev_idx]) or np.isnan(vol_ratio[prev_idx]) or \
               np.isnan(ma_fast[prev_idx]) or np.isnan(ma_slow[prev_idx]) or np.isnan(ma_trend[prev_idx]) or \
               np.isnan(rsi_v[prev_idx]) or np.isnan(macd_hist[prev_idx]) or np.isnan(press_s[prev_idx]) or \
               (prev_idx - 3 < 0):
                continue

            # Layer 1: regime
            regime = 0
            if vol_ratio[prev_idx] >= i_vol_exp and adx_v[prev_idx] < i_adx_trend:
                regime = 3
            elif adx_v[prev_idx] >= i_adx_trend:
                regime = 1
            elif vol_ratio[prev_idx] <= i_vol_con:
                regime = 2

            trending = (regime == 1)
            di_bull = p_di_v[prev_idx] > m_di_v[prev_idx]
            di_bear = m_di_v[prev_idx] > p_di_v[prev_idx]

            # Layer 2: bias
            stack_up = (ma_fast[prev_idx] > ma_slow[prev_idx]) and (ma_slow[prev_idx] > ma_trend[prev_idx])
            stack_dn = (ma_fast[prev_idx] < ma_slow[prev_idx]) and (ma_slow[prev_idx] < ma_trend[prev_idx])
            above_str = (close_p[prev_idx] > ma_fast[prev_idx]) and (close_p[prev_idx] > ma_slow[prev_idx])
            below_str = (close_p[prev_idx] < ma_fast[prev_idx]) and (close_p[prev_idx] < ma_slow[prev_idx])

            bull_bias = 0.0
            if stack_up:
                bull_bias += 30.0
            if above_str:
                bull_bias += 20.0
            if close_p[prev_idx] > ma_trend[prev_idx]:
                bull_bias += 20.0

            bear_bias = 0.0
            if stack_dn:
                bear_bias += 30.0
            if below_str:
                bear_bias += 20.0
            if close_p[prev_idx] < ma_trend[prev_idx]:
                bear_bias += 20.0

            bias_bull = bull_bias >= i_bias_thresh
            bias_bear = bear_bias >= i_bias_thresh

            # Layer 3: momentum
            rsi_bull_f = rsi_v[prev_idx] > i_rsi_bull
            rsi_bear_f = rsi_v[prev_idx] < i_rsi_bear
            rsi_mom_up = rsi_v[prev_idx] > rsi_v[prev_idx - 3]
            rsi_mom_dn = rsi_v[prev_idx] < rsi_v[prev_idx - 3]

            macd_bull = (macd_hist[prev_idx] > 0) and (macd_hist[prev_idx] > macd_hist[prev_idx - 1])
            macd_bear = (macd_hist[prev_idx] < 0) and (macd_hist[prev_idx] < macd_hist[prev_idx - 1])

            mom_bull = 0
            if rsi_bull_f:
                mom_bull += 1
            if rsi_mom_up:
                mom_bull += 1
            if macd_bull:
                mom_bull += 1

            mom_bear = 0
            if rsi_bear_f:
                mom_bear += 1
            if rsi_mom_dn:
                mom_bear += 1
            if macd_bear:
                mom_bear += 1

            mom_bull_ok = mom_bull >= 2
            mom_bear_ok = mom_bear >= 2

            # Layer 4: pressure gauge
            press_mom = press_s[prev_idx] - press_s[prev_idx - i_press_mom]
            press_bull = (press_s[prev_idx] > 0.5 + i_press_thr) or (press_mom > i_press_thr)
            press_bear = (press_s[prev_idx] < 0.5 - i_press_thr) or (press_mom < -i_press_thr)

            # Composite scoring
            bull_total = 0
            if trending and di_bull:
                bull_total += 2
            if bias_bull:
                bull_total += 1
            if mom_bull_ok:
                bull_total += 1
            if press_bull:
                bull_total += 1

            bear_total = 0
            if trending and di_bear:
                bear_total += 2
            if bias_bear:
                bear_total += 1
            if mom_bear_ok:
                bear_total += 1
            if press_bear:
                bear_total += 1

            # Cooldown logic
            bars_since_trade += 1
            cooldown_ok = bars_since_trade >= i_cooldown

            # Check entries
            long_entry = (bull_total >= 5) and trending and cooldown_ok and (pos <= 0)
            short_entry = (bear_total >= 5) and trending and cooldown_ok and (pos >= 0)

            triggered = False
            if long_entry:
                if pos == -1:
                    short_exits[i] = True
                entries[i] = True
                pos = 1
                bars_since_trade = 0
                triggered = True
            elif short_entry:
                if pos == 1:
                    exits[i] = True
                short_entries[i] = True
                pos = -1
                bars_since_trade = 0
                triggered = True

            # regime exit if not trending
            if not triggered and not trending and pos != 0:
                if pos == 1:
                    exits[i] = True
                else:
                    short_exits[i] = True
                pos = 0

        return entries, short_entries, exits, short_exits

    tr_nb_fn = tr_nb
    rma_nb_fn = rma_nb
    sma_nb_fn = sma_nb
    ema_nb_fn = ema_nb
    rsi_nb_fn = rsi_nb
    logic_loop_fn = logic_loop

    entries, short_entries, exits, short_exits = logic_loop(
        close_p, open_p, adx_v, p_di_v, m_di_v, vol_ratio,
        ma_fast, ma_slow, ma_trend, rsi_v, macd_hist, press_s
    )

    return vbt.Portfolio.from_signals(
        df['close'],
        entries=pd.Series(entries, index=df.index),
        short_entries=pd.Series(short_entries, index=df.index),
        exits=pd.Series(exits, index=df.index),
        short_exits=pd.Series(short_exits, index=df.index),
        price=df['open'],
        init_cash=1000000,
        fees=fees,
        slippage=0.0,
        upon_opposite_entry='reverse',
        accumulate=False,
        size=1.0,
        size_type='Amount'
    )
