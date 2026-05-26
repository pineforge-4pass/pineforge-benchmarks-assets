import pandas as pd
import numpy as np
import vectorbt as vbt
from numba import njit

def run_vbt(df: pd.DataFrame, fees: float = 0.001) -> vbt.Portfolio:
    close_p = df['close'].values
    open_p = df['open'].values
    high_p = df['high'].values
    low_p = df['low'].values
    volume_p = df['volume'].values
    n = len(df)

    # We need New York session active
    # time(timeframe.period, "0800-1600", "America/New_York")
    # Let's extract America/New_York timestamp
    if 'timestamp' in df.columns:
        dt = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
        # We need .dt accessor since it is a Series
        dt = dt.dt.tz_convert('America/New_York')
    elif isinstance(df.index, pd.DatetimeIndex):
        dt = df.index.tz_convert('America/New_York')
    else:
        # RangeIndex of ints? But wait, standard RangeIndex values are just 0, 1, 2...
        # If we interpret them as ms timestamps, they will all be 1970.
        # But we must have real timestamps if we want hour of day.
        # Let's check: does df have any datetime index or another column?
        # Actually, let's just use timezone New York hour/minute.
        # If no timestamp column and no datetime index, let's fall back to UTC time from pd.date_range
        # with 15m frequency starting at some date.
        dt = pd.date_range(start='2024-01-01', periods=n, freq='15min', tz='UTC').tz_convert('America/New_York')

    # active session hours: 08:00 to 16:00
    # Let's check minutes as well to make it strict: "0800-1600" means [08:00, 16:00)
    # Note: 15m bars inside the session are e.g. 08:00, 08:15 ... 15:45.
    # The bar representing 16:00 is not inside the session.
    # So time in minutes must be >= 8*60 and < 16*60
    if isinstance(dt, pd.Series):
        hours = dt.dt.hour.values
        minutes = dt.dt.minute.values
    else:
        hours = dt.hour.values
        minutes = dt.minute.values

    minutes_from_midnight = hours * 60 + minutes
    in_session_p = (minutes_from_midnight >= 8*60) & (minutes_from_midnight < 16*60)

    # Let's compute indicator functions
    @njit
    def rma_nb(arr, length):
        out = np.empty(len(arr))
        out[:] = np.nan
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
        alpha = 1.0 / length
        for i in range(first_idx + length, len(arr)):
            out[i] = alpha * arr[i] + (1 - alpha) * out[i-1]
        return out

    @njit
    def sma_nb(arr, length):
        out = np.empty(len(arr))
        out[:] = np.nan
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

    @njit
    def std_nb(arr, length):
        out = np.empty(len(arr))
        out[:] = np.nan
        first_idx = 0
        while first_idx < len(arr) and np.isnan(arr[first_idx]):
            first_idx += 1
        if len(arr) - first_idx < length:
            return out
        start_idx = first_idx + length - 1
        for i in range(start_idx, len(arr)):
            # compute standard deviation (population or sample?)
            # Pine ta.stdev is sample standard deviation
            sub = arr[i - length + 1 : i + 1]
            mean = np.mean(sub)
            sq_diff = 0.0
            for val in sub:
                sq_diff += (val - mean) ** 2
            out[i] = np.sqrt(sq_diff / (length - 1))
        return out

    @njit
    def tr_nb(high, low, close):
        out = np.empty(len(close))
        out[0] = high[0] - low[0]
        for i in range(1, len(close)):
            out[i] = max(high[i] - low[i], abs(high[i] - close[i-1]), abs(low[i] - close[i-1]))
        return out

    @njit
    def pivot_high_nb(high, length):
        # ta.pivothigh(high, 5, 5)
        # Returns the high of the pivot bar if it is a local maximum among 2*length + 1 bars
        # The pivot bar is at index i - length
        out = np.empty(len(high))
        out[:] = np.nan
        for i in range(2 * length, len(high)):
            target_val = high[i - length]
            is_pivot = True
            for j in range(i - 2 * length, i + 1):
                if j == i - length:
                    continue
                if high[j] >= target_val:
                    is_pivot = False
                    break
            if is_pivot:
                out[i] = target_val
        return out

    @njit
    def pivot_low_nb(low, length):
        out = np.empty(len(low))
        out[:] = np.nan
        for i in range(2 * length, len(low)):
            target_val = low[i - length]
            is_pivot = True
            for j in range(i - 2 * length, i + 1):
                if j == i - length:
                    continue
                if low[j] <= target_val:
                    is_pivot = False
                    break
            if is_pivot:
                out[i] = target_val
        return out

    # -------------------------------------------------------------------------
    # Pre-calculate Indicators
    # -------------------------------------------------------------------------
    # ATR
    tr_v = tr_nb(high_p, low_p, close_p)
    atr_v = rma_nb(tr_v, 14)

    # Pivot High & Low (strength = 5)
    ph_raw = pivot_high_nb(high_p, 5)
    pl_raw = pivot_low_nb(low_p, 5)

    # Volume Z-score
    vol_ma = sma_nb(volume_p, 20)
    vol_std = std_nb(volume_p, 20)
    vol_z = np.zeros(n)
    for i in range(n):
        if vol_std[i] > 0:
            vol_z[i] = (volume_p[i] - vol_ma[i]) / vol_std[i]

    # Cumulative Volume Delta (10-bar sum)
    # buy_vol: float = volume if close > open else volume * (close - low) / (high - low + 0.0001)
    # sell_vol: float = volume if close < open else volume * (high - close) / (high - low + 0.0001)
    vol_d = np.empty(n)
    for i in range(n):
        c = close_p[i]
        o = open_p[i]
        h = high_p[i]
        l = low_p[i]
        v = volume_p[i]
        if c > o:
            buy_vol = v
        else:
            buy_vol = v * (c - l) / (h - l + 0.0001)
        if c < o:
            sell_vol = v
        else:
            sell_vol = v * (h - c) / (h - l + 0.0001)
        vol_d[i] = buy_vol - sell_vol

    # Cum-delta 10-bar sum
    cum_d = np.empty(n)
    cum_d[:] = np.nan
    running_sum = 0.0
    for i in range(10):
        running_sum += vol_d[i]
    cum_d[9] = running_sum
    for i in range(10, n):
        running_sum = running_sum - vol_d[i - 10] + vol_d[i]
        cum_d[i] = running_sum

    # ADX regime
    up_mv = np.empty(n)
    up_mv[:] = np.nan
    dn_mv = np.empty(n)
    dn_mv[:] = np.nan
    for i in range(1, n):
        up_mv[i] = high_p[i] - high_p[i-1]
        dn_mv[i] = low_p[i-1] - low_p[i]

    p_dm_v = np.zeros(n)
    m_dm_v = np.zeros(n)
    for i in range(1, n):
        u = up_mv[i]
        d = dn_mv[i]
        if u > d and u > 0:
            p_dm_v[i] = u
        if d > u and d > 0:
            m_dm_v[i] = d

    tr_smo = rma_nb(tr_v, 14)
    p_di_v = np.zeros(n)
    m_di_v = np.zeros(n)
    dx_v = np.zeros(n)
    for i in range(n):
        if tr_smo[i] > 0:
            p_di_v[i] = 100 * rma_nb(p_dm_v, 14)[i] / tr_smo[i]
            m_di_v[i] = 100 * rma_nb(m_dm_v, 14)[i] / tr_smo[i]
        di_sum = p_di_v[i] + m_di_v[i]
        if di_sum > 0:
            dx_v[i] = 100 * abs(p_di_v[i] - m_di_v[i]) / di_sum

    adx_v = rma_nb(dx_v, 14)

    # -------------------------------------------------------------------------
    # Core Logic Loop
    # -------------------------------------------------------------------------
    @njit
    def logic_loop(
        close_p, open_p, high_p, low_p, in_session_p,
        atr_v, ph_raw, pl_raw, vol_z, cum_d, adx_v, p_di_v, m_di_v
    ):
        entries = np.zeros(n, dtype=np.bool_)
        short_entries = np.zeros(n, dtype=np.bool_)
        exits = np.zeros(n, dtype=np.bool_)
        short_exits = np.zeros(n, dtype=np.bool_)

        # Carried last-confirmed levels
        last_ph = np.nan
        last_pl = np.nan

        # FVG zone list tracking
        # Each FVG zone is stored as: top, bot, is_bull (1 for bull, 0 for bear)
        # We can store up to 30 zones in pre-allocated static arrays
        fvg_top = np.zeros(30)
        fvg_bot = np.zeros(30)
        fvg_is_bull = np.zeros(30, dtype=np.int8)
        fvg_count = 0

        pos = 0 # 1 for long, -1 for short, 0 for flat

        for i in range(2, n):
            # Check FVG events on bar i-1 (since FVG is detected on bar i-1 and carried)
            # bull_fvg_event = low[i-1] > high[i-3] and close[i-2] > open[i-2]
            bull_fvg_event = (low_p[i-1] > high_p[i-3]) and (close_p[i-2] > open_p[i-2])
            bear_fvg_event = (high_p[i-1] < low_p[i-3]) and (close_p[i-2] > open_p[i-2]) # Wait, close[1] < open[1] in Pine! Let's check:
            # Bear: high < low[2] and close[1] < open[1].
            # So: high_p[i-1] < low_p[i-3] and close_p[i-2] < open_p[i-2]
            bear_fvg_event = (high_p[i-1] < low_p[i-3]) and (close_p[i-2] < open_p[i-2])

            fvg_min_w = atr_v[i-1] * 0.3

            if bull_fvg_event and (low_p[i-1] - high_p[i-3]) >= fvg_min_w:
                # Add to zones
                if fvg_count < 30:
                    fvg_top[fvg_count] = low_p[i-1]
                    fvg_bot[fvg_count] = high_p[i-3]
                    fvg_is_bull[fvg_count] = 1
                    fvg_count += 1
                else:
                    # shift left
                    for k in range(29):
                        fvg_top[k] = fvg_top[k+1]
                        fvg_bot[k] = fvg_bot[k+1]
                        fvg_is_bull[k] = fvg_is_bull[k+1]
                    fvg_top[29] = low_p[i-1]
                    fvg_bot[29] = high_p[i-3]
                    fvg_is_bull[29] = 1

            if bear_fvg_event and (low_p[i-3] - high_p[i-1]) >= fvg_min_w:
                # Add to zones
                if fvg_count < 30:
                    fvg_top[fvg_count] = low_p[i-3]
                    fvg_bot[fvg_count] = high_p[i-1]
                    fvg_is_bull[fvg_count] = 0
                    fvg_count += 1
                else:
                    # shift left
                    for k in range(29):
                        fvg_top[k] = fvg_top[k+1]
                        fvg_bot[k] = fvg_bot[k+1]
                        fvg_is_bull[k] = fvg_is_bull[k+1]
                    fvg_top[29] = low_p[i-3]
                    fvg_bot[29] = high_p[i-1]
                    fvg_is_bull[29] = 0

            # At the current bar i, we check if low <= t and high >= b for any active zone
            in_bull_fvg = False
            in_bear_fvg = False
            for k in range(fvg_count):
                t = fvg_top[k]
                b = fvg_bot[k]
                s = fvg_is_bull[k]
                if low_p[i-1] <= t and high_p[i-1] >= b:
                    if s == 1:
                        in_bull_fvg = True
                    else:
                        in_bear_fvg = True

            # Pivot tracking
            # We look at ph_raw[prev_idx]
            prev_idx = i - 1
            if not np.isnan(ph_raw[prev_idx]):
                last_ph = ph_raw[prev_idx]
            if not np.isnan(pl_raw[prev_idx]):
                last_pl = pl_raw[prev_idx]

            pivot_break_up = (not np.isnan(last_ph)) and (close_p[prev_idx] > last_ph)
            pivot_break_dn = (not np.isnan(last_pl)) and (close_p[prev_idx] < last_pl)

            # Volume anomaly
            vol_anom_bull = (abs(vol_z[prev_idx]) > 2.0) and (close_p[prev_idx] > open_p[prev_idx])
            vol_anom_bear = (abs(vol_z[prev_idx]) > 2.0) and (close_p[prev_idx] < open_p[prev_idx])

            # Cum delta
            cd_up = cum_d[prev_idx] > 0
            cd_dn = cum_d[prev_idx] < 0

            # ADX trend
            trending_bull = (adx_v[prev_idx] > 25.0) and (p_di_v[prev_idx] > m_di_v[prev_idx])
            trending_bear = (adx_v[prev_idx] > 25.0) and (m_di_v[prev_idx] > p_di_v[prev_idx])

            # NY session
            in_session = in_session_p[prev_idx]

            # Long Setup
            long_setup = pivot_break_up and in_bull_fvg and (vol_anom_bull or cd_up) and trending_bull and in_session
            short_setup = pivot_break_dn and in_bear_fvg and (vol_anom_bear or cd_dn) and trending_bear and in_session

            triggered = False
            if long_setup and pos <= 0:
                if pos == -1:
                    short_exits[i] = True
                entries[i] = True
                pos = 1
                triggered = True
            elif short_setup and pos >= 0:
                if pos == 1:
                    exits[i] = True
                short_entries[i] = True
                pos = -1
                triggered = True

            # session end flat
            if not triggered and pos != 0:
                # "if not in_session and in_session[1] and strategy.position_size != 0: strategy.close_all"
                # so if in_session_p[prev_idx] is False but in_session_p[prev_idx-1] was True:
                if not in_session_p[prev_idx] and in_session_p[prev_idx - 1]:
                    if pos == 1:
                        exits[i] = True
                    else:
                        short_exits[i] = True
                    pos = 0

        return entries, short_entries, exits, short_exits

    entries, short_entries, exits, short_exits = logic_loop(
        close_p, open_p, high_p, low_p, in_session_p,
        atr_v, ph_raw, pl_raw, vol_z, cum_d, adx_v, p_di_v, m_di_v
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
