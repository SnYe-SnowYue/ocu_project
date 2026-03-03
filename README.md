# OCU ETF 專案（Merged: 新底層 + 新功能）

本專案已完成兩版本整合：
1. 基底採用 `SnYe` 新架構（Flask package + Blueprint + core/services 分層）。
2. 功能整合 `willy` 的 ETF 深度比較與首頁分析增量。

## 目前狀態
1. 已完成「新底層 + 新功能」程式整合。
2. 已補齊對應 schema（`stock_sectors`、`stock_name_map`）。
3. 已提供 Windows 友善的資料初始化流程（不需 Linux 指令）。
4. 已更新交接文件與合併紀錄。

## 專案結構

```text
.
├── app.py
├── ocu_app/
│   ├── __init__.py
│   ├── blueprints/
│   ├── core/
│   ├── services/
│   ├── templates/
│   └── static/
├── database/
│   ├── schema/schema.sql
│   ├── seed/etf_types.sql
│   ├── seed/etf_tickers.sql
│   ├── seed/stock_mappings.sql
│   └── backup/ocu_project_2025_1230.sql
├── scripts/init_db.py
├── docs/
│   ├── revamp.md
│   ├── onboarding_setup_test.md
│   ├── merge_summary_brief.md
│   └── merge_summary_detailed.md
├── .env.example
└── requirements.txt
```

## 核心功能
1. 使用者註冊/登入/個資設定。
2. 持股管理（新增、列表、刪除）。
3. ETF 推薦（風險等級映射）。
4. ETF 深度比較（成分股重疊、產業重疊、OII、振幅相關性）。
5. 首頁市場摘要與個人資產分析（7日/30日位階、產業配置圖）。

## 本機啟動流程

### 1) 啟動 MySQL（XAMPP）
至少啟動 `MySQL`。

### 2) 安裝依賴
```powershell
# 建立虛擬環境（使用系統預設 Python 3.10+）
python -m venv .venv

# 啟動虛擬環境
.\.venv\Scripts\Activate.ps1

# 若 PowerShell 阻擋執行腳本，先執行：
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 安裝套件
python -m pip install -r .\requirements.txt
```

### 3) 建立環境檔
```powershell
Copy-Item .\.env.example .\.env
```

### 4) 匯入資料庫（必要）
建議直接用內建腳本（Windows 可直接執行）：
```powershell
python .\scripts\init_db.py
```

此指令會自動：
1. 建立 `ocu_project` 資料庫。
2. 匯入 schema（資料表結構）。
3. 匯入 seed（ETF 類型、代號、股票映射）。
4. 匯入示範帳號與持股資料。

**示範帳號：** `demo` / `demo123`

此腳本會自動建立資料庫並匯入：
1. `database/schema/schema.sql`
2. `database/seed/etf_types.sql`
3. `database/seed/etf_tickers.sql`
4. `database/seed/stock_mappings.sql`

若要匯入額外示範資料，可再手動匯入 `database/backup/ocu_project_2025_1230.sql`（非必要）。

### 5) 啟動
```powershell
python .\app.py
```
預設：`http://127.0.0.1:5000`

## 快速檢查
```powershell
python -m compileall .\ocu_app
```

## 常見問題
1. `資料庫連線失敗`：檢查 XAMPP MySQL 與 `.env`。
2. `資料表不存在`：確認已匯入 `schema.sql`。
3. `比較頁缺少映射資料`：執行 `python .\scripts\init_db.py` 重新匯入 `stock_mappings.sql`。

## 文件入口
1. 重構紀錄：`docs/revamp.md`
2. 新手架設與測試：`docs/onboarding_setup_test.md`
3. 合併精簡版：`docs/merge_summary_brief.md`
4. 合併詳細版：`docs/merge_summary_detailed.md`
