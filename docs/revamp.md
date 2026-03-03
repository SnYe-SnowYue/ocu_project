# OCU Project Revamp 與整合紀錄

## 目的
1. 維持 `SnYe` 新底層架構與可維護性。
2. 併入 `willy` 版本中的新功能。
3. 同步更新 DB schema 與文件，避免交接落差。

## 架構面結果

### 保留的新底層
1. `app.py` 作為啟動入口。
2. `ocu_app/` 內以 Blueprint / core / services 分層。
3. 統一 DB 連線與錯誤處理模式。

### 併入的新功能
1. 推薦比較頁深度分析：
- 成分股重疊權重
- 產業曝險重疊
- OII 重疊強度
- 振幅相關性
2. 推薦頁搜尋輸入（ETF 代號或名稱）。
3. 首頁位階資訊（7日/30日高低點）與產業配置圖。

## 主要程式調整
1. `ocu_app/blueprints/recommend.py`：比較流程與指標整合。
2. `ocu_app/services/market_data.py`：新增 `get_price_position()`。
3. `ocu_app/__init__.py`：首頁資料彙整加入位階與產業分佈。
4. `ocu_app/templates/recommend.html`：比較輸入改為搜尋式。
5. `ocu_app/templates/compare_result.html`：報告頁升級。
6. `ocu_app/templates/index.html`：首頁分析區塊升級。

## DB 變更
1. `database/schema/schema.sql` 新增 `stock_sectors`。
2. `database/schema/schema.sql` 新增 `stock_name_map`。

說明：
上述兩表是成分股中文對照與產業分析必要依賴；若缺失，功能僅能退化顯示。

## 文件變更
1. `README.md`：更新為 merged 狀態與完整匯入步驟。
2. `docs/onboarding_setup_test.md`：新增合併後測試重點。
3. `docs/merge_summary_brief.md`：GitHub 用精簡版。
4. `docs/merge_summary_detailed.md`：GitHub 用詳細版。

## 驗證
1. 已執行：`python -m compileall .\ocu_app`（通過）。
2. 未執行：需 MySQL 與完整資料的端到端測試。
