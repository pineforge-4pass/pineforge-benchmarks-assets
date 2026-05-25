#include <pineforge/engine.hpp>
#include <pineforge/ta.hpp>
#include <pineforge/math.hpp>
#include <pineforge/series.hpp>
#include <pineforge/na.hpp>
#include <cstdint>
#include <cmath>
#include <algorithm>
#include <cstdlib>
#include <numeric>
#include <string>
#include <vector>
#include <tuple>
#include <memory>
#include <mutex>
#include <unordered_map>
#include <unordered_map>
#include <pineforge/color.hpp>
#include <pineforge/log.hpp>
#include <pineforge/str_utils.hpp>
#include <pineforge/session_time.hpp>

using namespace pineforge;

// --- syminfo derivation helpers (PineForge G2) ---
static inline std::string _pf_derive_prefix(const std::string& tickerid) {
    std::size_t colon = tickerid.find(':');
    return (colon == std::string::npos) ? tickerid : tickerid.substr(0, colon);
}

static inline std::string _pf_derive_main_tickerid(const std::string& tickerid) {
    // Strip trailing digits (optionally followed by '!') from the symbol part.
    // e.g. "CME_MINI:ES1!" -> "CME_MINI:ES", "NYMEX:CL2!" -> "NYMEX:CL"
    std::string result = tickerid;
    std::size_t colon = result.find(':');
    std::size_t start = (colon == std::string::npos) ? 0 : colon + 1;
    // Find end of base symbol (strip trailing digits + optional '!')
    std::size_t end = result.size();
    if (end > start && result[end - 1] == '!') {
        --end;
    }
    while (end > start && std::isdigit((unsigned char)result[end - 1])) {
        --end;
    }
    return result.substr(0, end);
}

static inline std::string _pf_derive_country(const std::string& tickerid) {
    // Lookup country by exchange prefix (text before ':').
    std::size_t colon = tickerid.find(':');
    std::string prefix = (colon == std::string::npos)
        ? tickerid : tickerid.substr(0, colon);
    static const std::unordered_map<std::string, std::string> _tbl = {
        {"AMEX", "US"},
        {"AQUIS", "UK"},
        {"ARCA", "US"},
        {"ASX", "AU"},
        {"B3", "BR"},
        {"BINANCE", "GLOBAL"},
        {"BITMEX", "GLOBAL"},
        {"BMF", "BR"},
        {"BMFBOVESPA", "BR"},
        {"BSE", "IN"},
        {"BYBIT", "GLOBAL"},
        {"CBOE", "US"},
        {"CBOT", "US"},
        {"CME", "US"},
        {"CME_MINI", "US"},
        {"COINBASE", "US"},
        {"COMEX", "US"},
        {"DERIBIT", "GLOBAL"},
        {"EURONEXT", "EU"},
        {"HKEX", "HK"},
        {"JSE", "ZA"},
        {"KOSPI", "KR"},
        {"KRAKEN", "GLOBAL"},
        {"KRX", "KR"},
        {"LSE", "UK"},
        {"MOEX", "RU"},
        {"NASDAQ", "US"},
        {"NSE", "IN"},
        {"NYMEX", "US"},
        {"NYSE", "US"},
        {"OKX", "GLOBAL"},
        {"OSE", "JP"},
        {"OTC", "US"},
        {"SGX", "SG"},
        {"SIX", "CH"},
        {"SSE", "CN"},
        {"SZSE", "CN"},
        {"TSE", "JP"},
        {"TSX", "CA"},
        {"UPBIT", "KR"},
        {"VENTURE", "CA"},
        {"XETRA", "DE"}
    };
    auto it = _tbl.find(prefix);
    return (it != _tbl.end()) ? it->second : na<std::string>();
}
// --- end syminfo derivation helpers ---

class GeneratedStrategy : public BacktestEngine {
public:
    ta::SMA _ta_sma_1;
    ta::EMA _ta_ema_2;
    ta::TR _ta_tr_3;
    ta::ATR _ta_atr_4;
    ta::RMA _ta_rma_5;
    ta::Crossover _ta_crossover_6;
    ta::Crossunder _ta_crossunder_7;
    Series<double> bprice;
    Series<bool> crossBcond;
    Series<bool> crossScond;
    Series<double> sprice;
    int length = 0;
    double mult = 0.0;
    double src = 0.0;
    double _exp_ = 0.0;
    std::string BandsStyle = std::string("");
    double atrlength = 0.0;
    double ma = 0.0;
    double rangema = 0.0;
    double upper = 0.0;
    double lower = 0.0;
    bool crossUpper = false;
    bool crossLower = false;
    bool cancelBcond = false;
    bool cancelScond = false;
    bool _ta_initialized_ = false;
    bool _inputs_initialized_ = false;

    explicit GeneratedStrategy() : _ta_sma_1(20), _ta_ema_2(20), _ta_tr_3(true), _ta_atr_4(10), _ta_rma_5(20) {
        initial_capital_ = 1000000.0;
        default_qty_type_ = QtyType::FIXED;
        default_qty_value_ = 1.0;
        pyramiding_ = 1;
        commission_type_ = CommissionType::PERCENT;
        commission_value_ = 0.0;
        slippage_ = 0;
    }

    void set_strategy_override(const std::string& key, const std::string& value) {
        if (key == "initial_capital") { initial_capital_ = std::stod(value); return; }
        if (key == "commission_value") { commission_value_ = std::stod(value); return; }
        if (key == "default_qty_value") { default_qty_value_ = std::stod(value); return; }
        if (key == "pyramiding") { pyramiding_ = std::stoi(value); return; }
        if (key == "slippage") { slippage_ = std::stoi(value); return; }
        if (key == "process_orders_on_close") { process_orders_on_close_ = (value == "true" || value == "1"); return; }
        if (key == "close_entries_rule") { close_entries_rule_any_ = (value == "ANY" || value == "any" || value == "1"); return; }
        if (key == "default_qty_type") {
            if (value == "fixed" || value == "strategy.fixed" || value == "0") default_qty_type_ = QtyType::FIXED;
            else if (value == "percent_of_equity" || value == "strategy.percent_of_equity" || value == "1") default_qty_type_ = QtyType::PERCENT_OF_EQUITY;
            else if (value == "cash" || value == "strategy.cash" || value == "2") default_qty_type_ = QtyType::CASH;
            return;
        }
        if (key == "commission_type") {
            if (value == "percent" || value == "strategy.commission.percent" || value == "0") commission_type_ = CommissionType::PERCENT;
            else if (value == "cash_per_order" || value == "strategy.commission.cash_per_order" || value == "1") commission_type_ = CommissionType::CASH_PER_ORDER;
            else if (value == "cash_per_contract" || value == "strategy.commission.cash_per_contract" || value == "2") commission_type_ = CommissionType::CASH_PER_CONTRACT;
            return;
        }
    }

    double esma_cs0(double source, int length) {
        double s = (is_first_tick_ ? _ta_sma_1.compute(source) : _ta_sma_1.recompute(source));
        double e = (is_first_tick_ ? _ta_ema_2.compute(source) : _ta_ema_2.recompute(source));
        return ((_exp_) ? (e) : (s));
    }

    void on_bar(const Bar& bar) override {
        if (!_inputs_initialized_) {
            length = get_input_int("length", 20);
            mult = get_input_double("Multiplier", 2.0);
            src = get_input_double("Source", current_bar_.close);
            _exp_ = get_input_double("Use Exponential MA", true);
            BandsStyle = get_input_string("Bands Style", std::string("Average True Range"));
            atrlength = get_input_double("ATR Length", 10);
            _inputs_initialized_ = true;
        }
        if (!_ta_initialized_) {
            _ta_sma_1 = ta::SMA(get_input_int("length", 20));
            _ta_ema_2 = ta::EMA(get_input_int("length", 20));
            _ta_atr_4 = ta::ATR(get_input_double("ATR Length", 10));
            _ta_rma_5 = ta::RMA(get_input_int("length", 20));
            _ta_initialized_ = true;
        }
        ma = esma_cs0(src, length);
        rangema = (((BandsStyle == std::string("True Range"))) ? ((is_first_tick_ ? _ta_tr_3.compute(current_bar_.high, current_bar_.low, current_bar_.close) : _ta_tr_3.recompute(current_bar_.high, current_bar_.low, current_bar_.close))) : ((((BandsStyle == std::string("Average True Range"))) ? ((is_first_tick_ ? _ta_atr_4.compute(current_bar_.high, current_bar_.low, current_bar_.close) : _ta_atr_4.recompute(current_bar_.high, current_bar_.low, current_bar_.close))) : ((is_first_tick_ ? _ta_rma_5.compute((current_bar_.high - current_bar_.low)) : _ta_rma_5.recompute((current_bar_.high - current_bar_.low)))))));
        upper = (ma + (rangema * mult));
        lower = (ma - (rangema * mult));
        crossUpper = (is_first_tick_ ? _ta_crossover_6.compute(src, upper) : _ta_crossover_6.recompute(src, upper));
        crossLower = (is_first_tick_ ? _ta_crossunder_7.compute(src, lower) : _ta_crossunder_7.recompute(src, lower));
        bprice.push(0.0);
        bprice.update(((crossUpper) ? ((current_bar_.high + syminfo_.mintick)) : ((is_na(bprice[1]) ? 0.0 : bprice[1]))));
        sprice.push(0.0);
        sprice.update(((crossLower) ? ((current_bar_.low - syminfo_.mintick)) : ((is_na(sprice[1]) ? 0.0 : sprice[1]))));
        crossBcond.push(false);
        crossBcond.update(((crossUpper) ? (true) : (crossBcond[1])));
        crossScond.push(false);
        crossScond.update(((crossLower) ? (true) : (crossScond[1])));
        cancelBcond = (crossBcond[0] && ((src < ma) || (current_bar_.high >= bprice[0])));
        cancelScond = (crossScond[0] && ((src > ma) || (current_bar_.low <= sprice[0])));
        if (cancelBcond) {
            strategy_cancel(std::string("KltChLE"));
        }
        if (crossUpper) {
            strategy_entry(std::string("KltChLE"), true, na<double>(), bprice[0], na<double>(), std::string("KltChLE"), "", 0, -1);
        }
        if (cancelScond) {
            strategy_cancel(std::string("KltChSE"));
        }
        if (crossLower) {
            strategy_entry(std::string("KltChSE"), false, na<double>(), sprice[0], na<double>(), std::string("KltChSE"), "", 0, -1);
        }
    }

};

extern "C" {
    void* strategy_create(const char* params_json) {
        return new GeneratedStrategy();
    }
    void run_backtest(void* s, Bar* bars, int n, ReportC* out) {
        auto* strat = static_cast<GeneratedStrategy*>(s);
        strat->run(bars, n);
        strat->fill_report(out);
    }
    void run_backtest_full(void* s, Bar* bars, int n,
                           const char* input_tf, const char* script_tf,
                           int bar_magnifier, int magnifier_samples,
                           int magnifier_dist,
                           ReportC* out) {
        auto* strat = static_cast<GeneratedStrategy*>(s);
        std::string itf = input_tf ? input_tf : "";
        std::string stf = script_tf ? script_tf : "";
        bool needs_full_run = (bar_magnifier != 0)
            || (!itf.empty() && !stf.empty() && itf != stf);
        if (!needs_full_run) {
            strat->run(bars, n);
        } else {
            strat->run(bars, n, itf, stf, bar_magnifier != 0, magnifier_samples,
                       static_cast<MagnifierDistribution>(magnifier_dist));
        }
        strat->fill_report(out);
    }
    void strategy_free(void* s) {
        delete static_cast<GeneratedStrategy*>(s);
    }
    void report_free(ReportC* report) {
        BacktestEngine::free_report(report);
    }
    void strategy_set_input(void* s, const char* key, const char* value) {
        if (!s || !key || !value) return;
        static_cast<GeneratedStrategy*>(s)->set_input(key, value);
    }
    void strategy_set_override(void* s, const char* key, const char* value) {
        if (!s || !key || !value) return;
        static_cast<GeneratedStrategy*>(s)->set_strategy_override(key, value);
    }
    void strategy_set_magnifier_volume_weighted(void* s, int on) {
        if (!s) return;
        static_cast<GeneratedStrategy*>(s)->set_magnifier_volume_weighted(on != 0);
    }
}
