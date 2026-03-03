from __future__ import annotations

from typing import Any, Dict

import yfinance as yf


def _as_float(value: Any) -> float | None:
    try:
        if isinstance(value, str):
            cleaned = value.replace("%", "").replace(",", "").strip()
            if not cleaned:
                return None
            return float(cleaned)
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_holdings_frame(frame: Any) -> dict[str, float]:
    if frame is None:
        return {}

    if not hasattr(frame, "empty") or not hasattr(frame, "iloc"):
        return {}

    if frame.empty:
        return {}

    columns = [str(col) for col in getattr(frame, "columns", [])]
    lowered = {col.strip().lower(): col for col in columns}

    name_col = None
    for candidate in ("name", "holding", "symbol", "ticker", "company"):
        if candidate in lowered:
            name_col = lowered[candidate]
            break

    weight_col = None
    for candidate in (
        "holding percent",
        "holding_pct",
        "weight",
        "portfolio weight",
        "% assets",
        "percent",
    ):
        if candidate in lowered:
            weight_col = lowered[candidate]
            break

    items: list[tuple[Any, Any]] = []
    if name_col and weight_col:
        items = list(zip(frame[name_col], frame[weight_col]))
    elif len(columns) >= 2:
        items = list(zip(frame.iloc[:, 0], frame.iloc[:, 1]))
    elif len(columns) == 1 and hasattr(frame, "index"):
        items = list(zip(frame.index, frame.iloc[:, 0]))

    result: dict[str, float] = {}
    for raw_name, raw_weight in items:
        name = str(raw_name).strip()
        if not name:
            continue

        numeric_weight = _as_float(raw_weight)
        if numeric_weight is None:
            continue

        percent_weight = numeric_weight * 100 if numeric_weight <= 1 else numeric_weight
        if percent_weight <= 0:
            continue
        result[name] = percent_weight

    return result


def get_top_holdings_weights(ticker_yfinance: str) -> dict[str, float]:
    try:
        ticker = yf.Ticker(ticker_yfinance)
    except Exception:
        return {}

    candidates: list[Any] = []

    try:
        funds_data = getattr(ticker, "funds_data", None)
        if funds_data is not None:
            candidates.append(getattr(funds_data, "top_holdings", None))
            candidates.append(getattr(funds_data, "holdings", None))
    except Exception:
        pass

    try:
        get_funds_data = getattr(ticker, "get_funds_data", None)
        if callable(get_funds_data):
            payload = get_funds_data()
            candidates.append(getattr(payload, "top_holdings", None))
            candidates.append(getattr(payload, "holdings", None))
    except Exception:
        pass

    for frame in candidates:
        parsed = _parse_holdings_frame(frame)
        if parsed:
            return parsed

    return {}


def _safe_round(value: Any, digits: int = 2) -> float:
    try:
        return round(float(value), digits)
    except (TypeError, ValueError):
        return 0.0


def get_etf_snapshot(
    ticker_yfinance: str,
    one_year_period: str = "1y",
    recent_period: str = "5d",
) -> Dict[str, float]:
    """
    回傳 ETF 所需展示資料，集中處理外部資料錯誤，避免頁面因為 yfinance 異常而崩潰。
    """
    snapshot = {
        "current_price": 0.0,
        "open_price": 0.0,
        "change_percent": 0.0,
        "yesterday_close": 0.0,
        "annual_return": 0.0,
        "amplitude": 0.0,
    }

    try:
        ticker = yf.Ticker(ticker_yfinance)
        yearly_hist = ticker.history(period=one_year_period)
        recent_hist = ticker.history(period=recent_period)

        if yearly_hist.empty and recent_hist.empty:
            return snapshot

        latest_source = yearly_hist if not yearly_hist.empty else recent_hist
        latest_row = latest_source.iloc[-1]

        current_price = float(latest_row.get("Close", 0.0))
        open_price = float(latest_row.get("Open", 0.0))

        snapshot["current_price"] = _safe_round(current_price)
        snapshot["open_price"] = _safe_round(open_price)

        if not yearly_hist.empty:
            price_col = "Adj Close" if "Adj Close" in yearly_hist.columns else "Close"
            start_price = float(yearly_hist[price_col].iloc[0])
            end_price = float(yearly_hist[price_col].iloc[-1])
            if start_price > 0:
                snapshot["annual_return"] = _safe_round(
                    ((end_price - start_price) / start_price) * 100
                )

        for source in (yearly_hist, recent_hist):
            if not source.empty and len(source) >= 2:
                previous_close = float(source["Close"].iloc[-2])
                if previous_close <= 0:
                    continue

                high_price = float(source["High"].iloc[-1])
                low_price = float(source["Low"].iloc[-1])
                change_percent = ((current_price - previous_close) / previous_close) * 100
                amplitude = ((high_price - low_price) / previous_close) * 100

                snapshot["yesterday_close"] = _safe_round(previous_close)
                snapshot["change_percent"] = _safe_round(change_percent)
                snapshot["amplitude"] = _safe_round(amplitude)
                break

        return snapshot
    except Exception:
        return snapshot


def get_price_position(ticker_yfinance: str) -> dict[str, bool]:
    """
    回傳目前價格是否接近 7 日/30 日高低點。
    """
    default_result = {
        "is_7d_high": False,
        "is_7d_low": False,
        "is_30d_high": False,
        "is_30d_low": False,
    }

    try:
        history = yf.Ticker(ticker_yfinance).history(period="1mo")
        if history.empty:
            return default_result

        latest_close = float(history["Close"].iloc[-1])
        if latest_close <= 0:
            return default_result

        recent_7 = history.tail(7)
        high_7 = float(recent_7["High"].max()) if not recent_7.empty else latest_close
        low_7 = float(recent_7["Low"].min()) if not recent_7.empty else latest_close
        high_30 = float(history["High"].max())
        low_30 = float(history["Low"].min())
        tolerance = latest_close * 0.003

        return {
            "is_7d_high": abs(latest_close - high_7) <= tolerance,
            "is_7d_low": abs(latest_close - low_7) <= tolerance,
            "is_30d_high": abs(latest_close - high_30) <= tolerance,
            "is_30d_low": abs(latest_close - low_30) <= tolerance,
        }
    except Exception:
        return default_result
