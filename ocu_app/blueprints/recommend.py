import math

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
import pandas as pd
import yfinance as yf

from ..core.config import AppConfig
from ..core.decorators import login_required
from ..core.models import DatabaseConnectionError, get_db_connection
from ..services.market_data import get_top_holdings_weights

recommend_bp = Blueprint("recommend", __name__)

ACTIVE_KEYWORDS = ("主動", "動力", "多空", "絕對報酬")


def _get_holdings(symbol: str) -> dict[str, float]:
    try:
        return get_top_holdings_weights(symbol)
    except Exception:
        return {}


def _detect_etf_type(name: str) -> str:
    if any(keyword in name for keyword in ACTIVE_KEYWORDS):
        return "主動型"
    if "正2" in name or "槓桿" in name:
        return "槓桿型"
    if "反1" in name or "反向" in name:
        return "反向型"
    return "被動型"


@recommend_bp.route("/recommend")
@login_required
def recommend_home():
    user_risk = session.get("risk_level", "中風險")
    risk_map = AppConfig.RISK_TYPE_MAP
    target_types = risk_map.get(user_risk, risk_map.get("中風險", (2,)))
    recommend_limit = max(1, int(AppConfig.RECOMMEND_ETF_LIMIT))

    db = None
    try:
        db = get_db_connection()
        with db.cursor() as cursor:
            format_strings = ",".join(["%s"] * len(target_types))
            cursor.execute(
                f"""
                SELECT t.name, t.ticker, t.ticker_yfinance, ty.name AS type_name
                FROM etf_tickers t
                JOIN etf_types ty ON t.types = ty.id
                WHERE t.types IN ({format_strings})
                LIMIT {recommend_limit}
                """,
                tuple(target_types),
            )
            recommended_etfs = cursor.fetchall()

            cursor.execute(
                """
                SELECT t.name, t.ticker, t.ticker_yfinance, ty.name AS type_name
                FROM etf_tickers t
                JOIN etf_types ty ON t.types = ty.id
                ORDER BY ty.name ASC, t.ticker ASC
                """
            )
            all_etfs = cursor.fetchall()

        return render_template(
            "recommend.html",
            etfs=recommended_etfs,
            all_etfs=all_etfs,
            user_risk=user_risk,
        )
    except DatabaseConnectionError as exc:
        current_app.logger.exception("Database connection failed: %s", exc)
        flash("資料庫連線失敗，請確認 XAMPP MySQL 與 .env 設定。", "danger")
        return redirect(url_for("home"))
    except Exception as exc:
        current_app.logger.exception("Load recommendation failed: %s", exc)
        flash("推薦資料讀取失敗，請稍後再試。", "danger")
        return redirect(url_for("home"))
    finally:
        if db:
            db.close()


@recommend_bp.route("/compare", methods=["POST"])
@login_required
def compare_etfs():
    ticker1 = (request.form.get("etf1") or "").strip()
    ticker2 = (request.form.get("etf2") or "").strip()

    if not ticker1 or not ticker2:
        flash("請選擇兩檔 ETF。", "warning")
        return redirect(url_for("recommend.recommend_home"))

    if ticker1 == ticker2:
        flash("請選擇不同的兩檔 ETF 進行比較。", "warning")
        return redirect(url_for("recommend.recommend_home"))

    db = None
    try:
        db = get_db_connection()
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT ticker, ticker_yfinance, name
                FROM etf_tickers
                WHERE ticker_yfinance = %s OR ticker_yfinance = %s
                """,
                (ticker1, ticker2),
            )
            detail_etfs = cursor.fetchall()

            try:
                cursor.execute(
                    """
                    SELECT m.name_en, m.name_cn, m.stock_ticker, s.sector_name
                    FROM stock_name_map m
                    LEFT JOIN stock_sectors s ON m.sector_id = s.id
                    """
                )
                mapping_rows = cursor.fetchall()
            except Exception:
                mapping_rows = []

        ticker_name_map = {item["ticker_yfinance"]: item["name"] for item in detail_etfs}
        etf1_name = ticker_name_map.get(ticker1, ticker1)
        etf2_name = ticker_name_map.get(ticker2, ticker2)

        name_lookup = {
            row["name_en"]: f'{row["name_cn"]} ({row["stock_ticker"]})'
            for row in mapping_rows
            if row.get("name_en") and row.get("name_cn") and row.get("stock_ticker")
        }
        sector_lookup = {
            row["name_en"]: (row.get("sector_name") or "其他")
            for row in mapping_rows
            if row.get("name_en")
        }

        holdings1 = _get_holdings(ticker1)
        holdings2 = _get_holdings(ticker2)
        common_stocks = sorted(set(holdings1) & set(holdings2))

        overlap_weight = 0.0
        overlap_intensity_score = 0.0
        overlap_details: list[dict[str, str | float]] = []
        sector_summary: dict[str, dict[str, float | list[str]]] = {}

        for stock in common_stocks:
            w1 = holdings1[stock] * 100
            w2 = holdings2[stock] * 100
            current_overlap = min(w1, w2)
            overlap_weight += current_overlap
            overlap_intensity_score += current_overlap**2

            sector_name = sector_lookup.get(stock, "其他")
            display_name = name_lookup.get(stock, stock)

            if sector_name not in sector_summary:
                sector_summary[sector_name] = {"total": 0.0, "stocks": []}

            sector_summary[sector_name]["total"] += current_overlap
            sector_summary[sector_name]["stocks"].append(display_name)

            overlap_details.append(
                {
                    "name": display_name,
                    "sector": sector_name,
                    "w1": round(w1, 2),
                    "w2": round(w2, 2),
                }
            )

        final_intensity = round(math.sqrt(overlap_intensity_score), 2)
        if final_intensity > 15:
            intensity_label = "極高 (風險集中)"
            intensity_color = "text-danger"
        elif final_intensity > 5:
            intensity_label = "中等"
            intensity_color = "text-warning"
        else:
            intensity_label = "低 (分散良好)"
            intensity_color = "text-success"

        sorted_sector_analysis = sorted(
            [
                {
                    "label": sector_name,
                    "value": round(float(values["total"]), 2),
                    "stock_list": ", ".join(values["stocks"]),
                }
                for sector_name, values in sector_summary.items()
            ],
            key=lambda item: item["value"],
            reverse=True,
        )

        overlap_details.sort(key=lambda item: min(item["w1"], item["w2"]), reverse=True)

        compare_period = AppConfig.COMPARE_PERIOD
        df1 = yf.Ticker(ticker1).history(period=compare_period)
        df2 = yf.Ticker(ticker2).history(period=compare_period)

        corr = None
        if not df1.empty and not df2.empty:
            for dataframe in (df1, df2):
                dataframe["y_close"] = dataframe["Close"].shift(1)
                dataframe["amplitude"] = (
                    (dataframe["High"] - dataframe["Low"]) / dataframe["y_close"] * 100
                )

            df1 = df1.reset_index()[["Date", "amplitude"]]
            df2 = df2.reset_index()[["Date", "amplitude"]]
            merged = pd.merge(df1, df2, on="Date", suffixes=("_1", "_2"))
            if not merged.empty:
                corr = merged["amplitude_1"].corr(merged["amplitude_2"])
                corr = None if corr is None or pd.isna(corr) else round(float(corr), 3)

        return render_template(
            "compare_result.html",
            etf1_name=etf1_name,
            etf2_name=etf2_name,
            amplitude_corr=corr,
            overlap_weight=round(overlap_weight, 2),
            overlap_details=overlap_details,
            sector_analysis=sorted_sector_analysis,
            final_intensity=final_intensity,
            intensity_label=intensity_label,
            intensity_color=intensity_color,
            etf1_type=_detect_etf_type(etf1_name),
            etf2_type=_detect_etf_type(etf2_name),
        )
    except DatabaseConnectionError as exc:
        current_app.logger.exception("Database connection failed: %s", exc)
        flash("資料庫連線失敗，請確認 XAMPP MySQL 與 .env 設定。", "danger")
    except Exception as exc:
        current_app.logger.exception("ETF comparison failed: %s", exc)
        flash("比較失敗，請稍後再試。", "danger")
    finally:
        if db:
            db.close()

    return redirect(url_for("recommend.recommend_home"))
