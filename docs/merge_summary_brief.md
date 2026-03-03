# Merge Summary (Brief)

## 目標
把 `SnYe` 新底層（Flask package 架構）與 `willy` 的新功能整合為單一可維護版本。

## 已完成
1. 以 `SnYe專題` 作為主分支，保留新底層與既有藍圖結構。
2. 合併推薦比較新功能：
- ETF 成分股重疊權重
- 產業曝險重疊分析
- 重疊強度指數（OII）
- 振幅相關性分析
3. 更新推薦頁輸入體驗：支援輸入 ETF 代號/名稱搜尋（datalist）。
4. 更新比較結果頁：改為深度診斷報告版面（含摘要、明細、產業區塊）。
5. 合併首頁新功能：
- 7日/30日價位位階標籤
- 個人持股產業配置圓餅圖
6. 補齊新功能所需 schema：新增 `stock_sectors`、`stock_name_map`。
7. 全專案文件同步更新（README、重構紀錄、新手手冊、合併紀錄）。

## 主要變更檔案
1. `ocu_app/blueprints/recommend.py`
2. `ocu_app/templates/recommend.html`
3. `ocu_app/templates/compare_result.html`
4. `ocu_app/services/market_data.py`
5. `ocu_app/__init__.py`
6. `ocu_app/templates/index.html`
7. `database/schema/schema.sql`

## 驗證結果
1. `python -m compileall .\ocu_app`：通過。
2. 受限於本機環境（未啟動 MySQL / 未匯入資料），未執行端到端功能測試。

## 部署前必要動作
1. 執行 `python .\scripts\init_db.py`（自動匯入 schema + seed，含 `stock_sectors`、`stock_name_map`）。
2. 視需求加匯 `database/backup/ocu_project_2025_1230.sql`（示範資料）。
3. 再啟動 Flask 進行推薦比較與首頁圖表驗證。
