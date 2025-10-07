# Project Dashboard 一個輕量級的本地專案 Web儀表板

這是一個輕量級的本地 Web 儀表板，旨在幫助開發者快速總覽、管理存放在單一目錄下的眾多專案。

## 1. 用途 (Purpose)

對於習慣將多個專案（無論大小、語言）存放在同一個根目錄下的開發者，此工具可以解決以下痛點：

- **快速視覺化**：將雜亂的資料夾列表轉換為整潔的資訊卡片網格。
- **提供核心資訊**：無需進入每個資料夾，即可快速了解專案的用途（來自 README 的標題）、主要技術棧（語言成分分析）以及版本控制狀態。
- **動態搜尋**：提供即時搜尋功能，幫助您在數十個專案中快速定位目標。
- **狀態監控**：可選的 Git 狀態掃描功能，讓您一目了然地知道哪些專案有未提交的修改、哪些需要與遠端同步。

## 2. 技術要點 (Key Technologies)

- **後端 (Backend)**:
  - **Python 3**: 作為主要的開發語言。
  - **Flask**: 一個輕量的 WSGI Web 應用程式框架，用於提供 API 和前端頁面。
  - **標準庫**: 使用 `os` 模組進行檔案系統掃描，`subprocess` 模組與 Git 進行互動。

- **前端 (Frontend)**:
  - **HTML5 / CSS3**: 標準的網頁結構與樣式。
  - **JavaScript (Vanilla)**: 無需任何框架，用於從後端 API 獲取資料、動態渲染頁面以及處理使用者互動。
  - **Bootstrap 5**: 用於快速建構美觀、響應式的 UI 介面，例如卡片、徽章和開關。

## 3. 安裝與使用 (Installation & Usage)

**步驟 1: 進入專案目錄**
```bash
cd /path/to/your/project_dashboard
```

**步驟 2: (建議) 建立並啟用虛擬環境**
```bash
python3 -m venv venv
source venv/bin/activate
```

**步驟 3: 安裝依賴套件**
```bash
pip install -r requirements.txt
```

**步驟 4: (重要) 設定掃描路徑**
打開 `app.py` 檔案，找到 `SCAN_PATH` 變數，並將其值修改為您存放所有專案的根目錄絕對路徑。
```python
# --- Configuration ---
SCAN_PATH = "/path/to/your/projects/folder" 
```

**步驟 5: 啟動應用程式**
```bash
python3 app.py
```

**步驟 6: 開啟瀏覽器**
在您的網頁瀏覽器中訪問 `http://127.0.0.1:5001`，即可看到您的專案儀表板。

## 4. 可能的擴展功能 (Possible Extensions)

這個工具可以作為一個基礎，擴展出更多實用的功能：

- **專案快捷操作**: 在每個卡片上新增按鈕，用於執行常用指令，例如 `git pull`、`docker-compose up`、`npm install` 等。
- **詳細資訊頁面**: 點擊卡片可以跳轉到一個專案的詳細頁面，完整顯示 `README.md` 內容、檔案列表，甚至是一個簡易的程式碼預覽器。
- **設定檔**: 將 `SCAN_PATH`、語言顏色等設定移到一個獨立的 `config.json` 或 `config.ini` 檔案中，使其更容易配置。
- **掃描結果快取**: 對於專案數量極多的使用者，可以加入快取機制，將掃描結果暫存幾分鐘，避免每次刷新都重新掃描，加快載入速度。
- **進階篩選**: 新增依據程式語言、Git 狀態或其他元資料進行篩選的選項。

## 5. 專案檔案結構
```bash
project_dashboard
├── app.py
├── README.md
├── requirements.txt
└── templates
    └── index.html

2 directories, 4 files
```
