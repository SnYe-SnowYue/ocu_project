# OCU 專案新手上手：架設與測試指南（Merged 版）

本指南用於「已合併版本（新底層 + 新功能）」的本機建置與驗證。

## 0) 先備條件
1. XAMPP（至少啟動 MySQL）。
2. Python 3.10+。
3. 可使用終端機與 phpMyAdmin。

## 1) 安裝與環境設定

```powershell
# 建立虛擬環境（使用系統預設 Python 3.10+）
python -m venv .venv

# 啟動虛擬環境
.\.venv\Scripts\Activate.ps1

# 安裝套件
python -m pip install -r .\requirements.txt

# 複製環境設定檔
Copy-Item .\.env.example .\.env
```

若被 PowerShell 擋住啟用腳本：
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## 2) 匯入資料庫（合併版本必要順序）
建議直接執行：
```powershell
python .\scripts\init_db.py
```

此命令會自動建立 `ocu_project`，並匯入：
1. `database/schema/schema.sql`（資料庫結構）
2. `database/seed/etf_types.sql`（ETF 類型）
3. `database/seed/etf_tickers.sql`（ETF 代號）
4. `database/seed/stock_mappings.sql`（股票映射）
5. `database/backup/ocu_project_2025_1230.sql`（示範帳號與持股）

**示範帳號：** `demo` / `demo123`

## 3) 啟動
```powershell
python .\app.py
```
預設網址：`http://127.0.0.1:5000`

## 4) Smoke Test（合併後）
1. 註冊、登入、登出流程正常。
2. 首頁 `/index` 能顯示市場焦點與個人持股。
3. 首頁可看到位階標籤（7日/30日）。
4. 首頁產業配置圖可載入（若有持股與映射資料）。
5. 推薦頁 `/recommend/recommend` 可顯示推薦卡片。
6. 推薦頁比較區可輸入 ETF 代號或名稱。
7. 比較結果頁可看到：
- 振幅相關性
- 成分股重疊權重
- OII 指標
- 共同持股與產業明細

## 5) 快速檢測命令
```powershell
python -m compileall .\ocu_app
```

## 6) 常見問題
1. `Table ... doesn't exist`：通常是 `schema.sql` 或映射資料未匯入完成。
2. 推薦比較顯示資料不足：通常是 ETF 歷史資料或持股資料不足。
3. 首頁沒有產業圖：通常是尚未建立持股，或尚未執行 `python .\scripts\init_db.py` 完成映射資料匯入。
