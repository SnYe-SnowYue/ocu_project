# Merge Summary (Detailed)

## 合併範圍
本次合併採用「新底層優先」策略：
1. 基底：`SnYe專題`（Flask package、Blueprint 分層、核心設定與錯誤處理）。
2. 功能增量來源：`willy專題`（推薦比較深度分析、首頁視覺與分析功能）。

## 策略與原則
1. 不回退 `SnYe` 的架構與錯誤處理模式。
2. 功能移植優先對齊現有模組邊界（`blueprints`、`services`、`templates`）。
3. 新功能若依賴舊資料表，需同步補 schema 並保留容錯。

## 核心程式調整

### 1) 推薦比較模組（`recommend`）
檔案：`ocu_app/blueprints/recommend.py`

已整合能力：
1. 推薦列表維持風險映射邏輯，並保留新架構設定來源（`AppConfig`）。
2. 比較流程新增成分股重疊分析：
- 抓取兩檔 ETF 持股
- 計算共同持股與最小權重重疊值
- 彙整總重疊權重
3. 新增產業重疊分析：
- 使用 `stock_name_map` + `stock_sectors` 建立名稱與產業映射
- 產出各產業的重疊曝險與成分股明細
4. 新增 OII（Overlap Intensity Index）：
- 對重疊權重平方和開根號
- 以門檻輸出風險等級標籤
5. 保留振幅相關性計算（`COMPARE_PERIOD`），與上述指標一起輸出。
6. 保留 `login_required` 與 DB 例外處理。

### 2) 推薦頁與比較結果模板
檔案：
1. `ocu_app/templates/recommend.html`
2. `ocu_app/templates/compare_result.html`

調整內容：
1. 推薦頁比較輸入改為可搜尋模式（`input + datalist`）。
2. 保留「加入比對」快捷填入行為。
3. 比較結果頁升級為診斷報告：
- 振幅同步程度
- 成分股重疊權重
- OII 強度
- 共同持股明細表
- 共同持股產業曝險區塊

### 3) 首頁資料與市場服務
檔案：
1. `ocu_app/services/market_data.py`
2. `ocu_app/__init__.py`
3. `ocu_app/templates/index.html`

調整內容：
1. 新增 `get_price_position()`，提供 7日/30日高低位階判斷。
2. `home()` 在市場焦點與個人持股資料中加入位階資訊。
3. `home()` 對個人持股彙整產業分佈資料（供首頁圖表使用）。
4. 首頁模板加入：
- 位階狀態 badge
- 產業配置 doughnut chart（Chart.js）

## 資料庫與相容性

### schema 補強
檔案：`database/schema/schema.sql`

新增：
1. `stock_sectors`
2. `stock_name_map`

原因：
`willy` 新功能依賴這兩張表做成分股中文名稱與產業映射。若只合併程式不補 schema，會在 DB 查詢時缺表。

### 容錯處理
在比較邏輯中，映射資料查詢包在例外處理內。即使對照資料尚未匯入，系統仍可退化顯示（以英文名/其他產業），不會直接中斷流程。

## 文件更新
已更新：
1. `README.md`
2. `docs/revamp.md`
3. `docs/onboarding_setup_test.md`

已新增：
1. `docs/merge_summary_brief.md`
2. `docs/merge_summary_detailed.md`

## 檢測與限制

### 已執行
1. `python -m compileall .\ocu_app`
- 結果：通過（無 Python 語法錯誤）。

### 尚未執行（環境限制）
1. 端到端功能測試（需可用 MySQL 與完整資料匯入）。
2. 真實資料源整合測試（需連線 yfinance 與網路可用）。

## 上線/交付前檢查清單
1. 執行 `python .\scripts\init_db.py`（自動建立 DB 並匯入 schema 與 seed）。
2. 視需求匯入 `database/backup/ocu_project_2025_1230.sql`（示範資料）。
3. 啟動專案並手動驗證：
- `/recommend/recommend`：可完成兩檔 ETF 深度比較
- `/index`：可顯示位階狀態與產業配置圖
4. 完成 Smoke Test 後再推送到主分支。
