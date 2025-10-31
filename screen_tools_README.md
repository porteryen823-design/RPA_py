# Screen Tools - 螢幕工具程式

## 功能概述

`screen_tools.py` 是一個功能完整的螢幕工具程式，提供螢幕擷取、標記、測量和 OCR 文字辨識等功能。

## 主要功能

### 1. 螢幕顯示與互動
- 顯示整個螢幕作為底圖
- 滑鼠移動時顯示十字線（長度 100 pixel，可切換顏色）
- 十字線旁邊即時顯示座標 (x, y)，根據螢幕象限調整顯示位置
- 視窗頂部顯示當前座標標籤

### 2. 點標記功能
- **Shift+F1**: 記錄第一點（藍色圓點標記）
- **Shift+F2**: 記錄第二點（綠色圓點標記），自動繪製紫色矩形
- **ESC 鍵**: 反向移除標記點（先移除第二點，再移除第一點）

### 3. 右鍵選單功能
- **1. 標示第一點**: 在滑鼠位置標示藍色圓點
- **2. 標示第二點 (並繪出兩點矩形)**: 在滑鼠位置標示綠色圓點並繪製紫色矩形
- **3. 存整個螢幕**: 儲存完整的螢幕截圖到 `image_temp/full_screenshot_YYYYMMDDHHMMSS.png`
- **4. 存框出矩形**: 儲存由兩個標記點定義的矩形區域到 `image_temp/rectangle_YYYYMMDDHHMMSS.png`
- **5. 存檔 (帶標記)**: 儲存包含所有標記的圖片到 `image_temp/screenshot_with_marks_YYYYMMDDHHMMSS.png`
- **6. 清除繪製矩形**: 清除所有繪製的矩形和標記點
- **7. 存十字線座標**: 將當前十字線位置的座標存入記憶體
- **8. 重新擷取螢幕**: 重新擷取螢幕並更新底圖
- **9. 滑鼠動作設定**: 開啟 PyQt5 滑鼠動作設定視窗（需要 PyQt5）
- **10. 設定粉紅色十字線**: 將十字線和座標文字設定為粉紅色
- **11. 設定藍色十字線**: 將十字線和座標文字設定為藍色
- **12. OCR 功能**: 當有標記矩形時，進行 OCR 文字辨識（需要 Tesseract）
- **13. 隱藏滑鼠設定**: 隱藏滑鼠動作設定視窗

### 4. OCR 文字辨識
- 支援中文繁體和英文文字辨識
- 辨識結果顯示在獨立視窗中
- 提供複製到剪貼簿功能
- **新增翻譯功能**：支援繁體中文、簡體中文翻譯成英文
- 翻譯按鈕位於 OCR 結果視窗中，可手動選擇翻譯方式
- 需要安裝 Tesseract OCR 引擎和 translate 套件

## 安裝需求

### Python 套件
```bash
pip install pyautogui pillow tkinter pytesseract translate
```

### 可選套件（用於進階功能）
```bash
pip install PyQt5  # 用於滑鼠動作設定功能
```

### Tesseract OCR 引擎（用於 OCR 功能）
1. 下載 Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
2. 安裝到預設路徑: `C:\Program Files\Tesseract-OCR\`
3. 或修改程式碼中的路徑設定

## 使用方法

1. 執行程式：
```bash
python screen_tools.py
```

2. 程式會顯示整個螢幕的視窗

3. 使用鍵盤和滑鼠進行操作：
   - 移動滑鼠查看十字線和座標
   - Shift+F1/F2 記錄點位
   - ESC 移除標記點
   - 右鍵開啟功能選單

4. OCR 使用：
   - 先標記兩個點定義辨識區域
   - 右鍵選單選擇 "OCR 功能"
   - 查看辨識結果並可複製到剪貼簿
   - **翻譯功能**：在 OCR 結果視窗中點擊翻譯按鈕
     - "繁體中文翻英文"：指定來源為繁體中文
     - "簡體中文翻英文"：指定來源為簡體中文
     - "自動翻譯"：自動檢測來源語言

## 檔案輸出

- **完整螢幕截圖**：`image_temp/full_screenshot_YYYYMMDDHHMMSS.png`
- **矩形區域截圖**：`image_temp/rectangle_YYYYMMDDHHMMSS.png`
- **帶標記截圖**：`image_temp/screenshot_with_marks_YYYYMMDDHHMMSS.png`
- OCR 結果：顯示在視窗中，可複製到剪貼簿

## 技術特點

- 使用 Tkinter 建立圖形介面
- PIL/Pillow 處理圖片操作
- PyAutoGUI 進行螢幕擷取
- Pytesseract + Tesseract 進行 OCR 辨識
- 支援動態圖形繪製和互動操作

## 注意事項

- OCR 功能需要額外安裝 Tesseract OCR 引擎
- 程式在 Windows 環境下測試
- 確保螢幕解析度設定正確
- 部分功能可能需要管理員權限

## 版本歷史

- v1.0: 基本螢幕工具功能
- v1.1: 新增 OCR 文字辨識功能
- v1.2: 新增 ESC 鍵反向移除功能和即時座標顯示
- v1.3: 新增十字線座標記憶功能和顏色切換功能，優化座標顯示位置根據螢幕象限
- v1.4: 新增多種螢幕截圖儲存選項（完整螢幕、矩形區域、帶標記圖片）
- v1.5: 新增 OCR 文字翻譯功能，支援繁體/簡體中文翻譯成英文