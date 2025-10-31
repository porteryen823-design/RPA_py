import pyautogui
import os
import datetime
import time
import threading
from PIL import Image, ImageTk, ImageDraw
import tkinter as tk
try:
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows 預設路徑
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("警告: pytesseract 未安裝，OCR 功能將無法使用")
print(f"OCR_AVAILABLE 狀態: {OCR_AVAILABLE}") # 新增這行來印出狀態
try:
    from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QComboBox, QHeaderView, QPushButton, QHBoxLayout, QCheckBox
    from PyQt5.QtCore import Qt
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False
    print("警告: PyQt5 未安裝，滑鼠動作設定功能將無法使用")
try:
    from translate import Translator
    translator = Translator(to_lang="en")
    TRANSLATION_AVAILABLE = True
except ImportError:
    TRANSLATION_AVAILABLE = False
    print("警告: translate 未安裝，翻譯功能將無法使用")

def screen_tools():
    # 截取整個螢幕作為底圖
    full_screenshot = pyautogui.screenshot()

    # 顯示視窗預覽整個螢幕底圖
    root = tk.Tk()
    root.title("螢幕工具 - 整個螢幕底圖")

    # 創建 Canvas 用於動態繪製
    canvas = tk.Canvas(root, width=full_screenshot.width, height=full_screenshot.height)
    canvas.pack()

    # 轉換為 Tkinter 格式
    tk_img = ImageTk.PhotoImage(full_screenshot)
    canvas.create_image(0, 0, anchor=tk.NW, image=tk_img)

    # 座標顯示標籤
    coord_label = tk.Label(root, text="(0, 0)", font=("Arial", 12), bg="yellow")
    coord_label.pack()

    mouse_window = None  # 滑鼠設定視窗實例
    app = None  # QApplication 實例
    # 記錄點的變數
    point1 = None
    point2 = None
    cross_length = 100
    cross_coords = []  # 存儲十字線座標的列表
    cross_color = "pink"  # 十字線顏色，預設粉紅色

    # 滑鼠移動事件
    def on_mouse_move(event):
        # 清除之前的粉紅色十字線和座標文字
        canvas.delete("pink_cross")
        canvas.delete("coord_text")

        # 畫新的十字線
        x, y = event.x, event.y
        canvas.create_line(x - cross_length//2, y, x + cross_length//2, y, fill=cross_color, width=2, tags="pink_cross")
        canvas.create_line(x, y - cross_length//2, x, y + cross_length//2, fill=cross_color, width=2, tags="pink_cross")

        # 根據螢幕中心決定座標顯示位置
        screen_center_x = full_screenshot.width // 2
        screen_center_y = full_screenshot.height // 2

        # 判斷象限並決定文字顯示位置
        if x >= screen_center_x and y < screen_center_y:  # 第一象限
            text_x = x - 50  # 顯示在第三象限對角
            text_y = y + 30
        elif x < screen_center_x and y < screen_center_y:  # 第二象限
            text_x = x + 50  # 顯示在第四象限對角
            text_y = y + 30
        elif x < screen_center_x and y >= screen_center_y:  # 第三象限
            text_x = x + 50  # 顯示在第一象限對角
            text_y = y - 30
        else:  # 第四象限
            text_x = x - 50  # 顯示在第二象限對角
            text_y = y - 30

        # 顯示座標文字
        canvas.create_text(text_x, text_y, text=f"({x}, {y})", fill=cross_color, font=("Arial", 10), tags="coord_text")

        # 更新座標顯示標籤
        coord_label.config(text=f"({x}, {y})")

    canvas.bind("<Motion>", on_mouse_move)

    # 鍵盤事件處理
    def on_key_press(event):
        nonlocal point1, point2
        if event.keysym == 'F1' and event.state & 0x1:  # Shift+F1
            x, y = root.winfo_pointerxy()
            rel_x = x - root.winfo_rootx()
            rel_y = y - root.winfo_rooty()
            point1 = (rel_x, rel_y)
            print(f"記錄第一點: ({rel_x}, {rel_y})")
            draw_point_marker(rel_x, rel_y, "blue", "point1")
        elif event.keysym == 'F2' and event.state & 0x1:  # Shift+F2
            x, y = root.winfo_pointerxy()
            rel_x = x - root.winfo_rootx()
            rel_y = y - root.winfo_rooty()
            point2 = (rel_x, rel_y)
            print(f"記錄第二點: ({rel_x}, {rel_y})")
            draw_point_marker(rel_x, rel_y, "green", "point2")
            if point1:
                draw_rectangle(point1, point2)
        elif event.keysym == 'Escape':  # ESC 鍵反向移除標記點
            if point2:
                canvas.delete("point2")
                point2 = None
                canvas.delete("user_rect")
                print("已移除第二點")
            elif point1:
                canvas.delete("point1")
                point1 = None
                print("已移除第一點")

    def draw_point_marker(x, y, color, tag):
        canvas.create_oval(x-5, y-5, x+5, y+5, fill=color, tags=tag)

    def draw_rectangle(p1, p2):
        canvas.delete("user_rect")
        x1, y1 = p1
        x2, y2 = p2
        canvas.create_rectangle(x1, y1, x2, y2, outline="purple", width=2, tags="user_rect")

    root.bind("<KeyPress>", on_key_press)

    # 右鍵選單
    def show_context_menu(event):
        menu = tk.Menu(root, tearoff=0)
        menu.add_command(label="1. 標示第一點", command=lambda: mark_point1(event))
        menu.add_command(label="2. 標示第二點 (並繪出兩點矩形)", command=lambda: mark_point2(event))
        menu.add_command(label="3. 存整個螢幕", command=save_full_screen)
        menu.add_command(label="4. 存框出矩形", command=save_rectangle)
        menu.add_command(label="5. 存檔 (帶標記)", command=save_image)
        menu.add_command(label="6. 清除繪製矩形", command=clear_rectangles)
        menu.add_separator()
        menu.add_command(label="7. 存十字線座標", command=lambda: save_cross_coords(event))
        if PYQT5_AVAILABLE:
            menu.add_command(label="9. 滑鼠動作設定", command=lambda: open_mouse_settings())
            menu.add_command(label="13. 隱藏滑鼠設定", command=hide_mouse_settings)
        else:
            menu.add_command(label="9. 滑鼠動作設定 (未安裝 PyQt5)", state="disabled")
        menu.add_command(label="8. 重新擷取螢幕", command=refresh_screenshot)
        menu.add_command(label="10. 設定粉紅色十字線", command=set_pink_cross)
        menu.add_command(label="11. 設定藍色十字線", command=set_blue_cross)
        if point1 and point2 and OCR_AVAILABLE:
            menu.add_command(label="12. OCR 功能", command=perform_ocr)
        elif not OCR_AVAILABLE:
            menu.add_command(label="12. OCR 功能 (未安裝)", state="disabled")
        menu.post(event.x_root, event.y_root)

    def mark_point1(event):
        nonlocal point1
        x, y = event.x, event.y
        point1 = (x, y)
        print(f"標示第一點: ({x}, {y})")
        draw_point_marker(x, y, "blue", "point1")

    def mark_point2(event):
        nonlocal point2
        x, y = event.x, event.y
        point2 = (x, y)
        print(f"標示第二點: ({x}, {y})")
        draw_point_marker(x, y, "green", "point2")
        if point1:
            draw_rectangle(point1, point2)

    def save_full_screen():
        # 儲存整個螢幕截圖
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        save_path = f"image_temp/full_screenshot_{timestamp}.png"
        os.makedirs("image_temp", exist_ok=True)
        full_screenshot.save(save_path)
        print(f"已儲存整個螢幕: {save_path}")

    def save_rectangle():
        if not point1 or not point2:
            print("需要先標記兩個點來定義矩形區域")
            return
        # 計算矩形區域
        x1, y1 = point1
        x2, y2 = point2
        left = min(x1, x2)
        top = min(y1, y2)
        right = max(x1, x2)
        bottom = max(y1, y2)
        # 從螢幕截圖中擷取區域
        region_img = full_screenshot.crop((left, top, right, bottom))
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        save_path = f"image_temp/rectangle_{timestamp}.png"
        os.makedirs("image_temp", exist_ok=True)
        region_img.save(save_path)
        print(f"已儲存矩形區域: {save_path}")

    def save_image():
        # 儲存當前 canvas 內容為圖片
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        save_path = f"image_temp/screenshot_with_marks_{timestamp}.png"
        os.makedirs("image_temp", exist_ok=True)
        # 創建新的圖片來儲存 canvas 內容
        img = Image.new("RGB", (full_screenshot.width, full_screenshot.height), "white")
        draw_img = ImageDraw.Draw(img)
        # 複製原始圖片
        img.paste(full_screenshot, (0, 0))
        # 繪製標記
        if point1:
            draw_img.ellipse([point1[0]-5, point1[1]-5, point1[0]+5, point1[1]+5], fill="blue")
        if point2:
            draw_img.ellipse([point2[0]-5, point2[1]-5, point2[0]+5, point2[1]+5], fill="green")
        if point1 and point2:
            draw_img.rectangle([point1[0], point1[1], point2[0], point2[1]], outline="purple", width=2)
        img.save(save_path)
        print(f"已儲存標記圖片: {save_path}")

    def clear_rectangles():
        canvas.delete("user_rect")
        canvas.delete("point1")
        canvas.delete("point2")
        nonlocal point1, point2
        point1 = None
        point2 = None
        print("已清除所有繪製矩形和標記點")

    def save_cross_coords(event):
        nonlocal cross_coords
        x, y = event.x, event.y
        cross_coords.append((x, y))
        print(f"已存十字線座標: ({x}, {y})，目前共有 {len(cross_coords)} 個座標")

    def set_pink_cross():
        nonlocal cross_color
        cross_color = "pink"
        print("十字線顏色已設定為粉紅色")

    def open_mouse_settings():
        nonlocal mouse_window, app
        print("正在開啟滑鼠動作設定視窗...")
        try:
            # 如果視窗已經存在，只顯示它
            if mouse_window is not None:
                mouse_window.show()
                mouse_window.raise_()
                print("滑鼠設定視窗已重新顯示")
                return

            # 創建 PyQt5 應用程式
            app = QApplication.instance()
            if app is None:
                app = QApplication([])
                print("已創建新的 QApplication 實例")

            # 創建滑鼠設定視窗
            mouse_window = MouseSettingsWindow(cross_coords)
            mouse_window.show()
            print("滑鼠設定視窗已顯示")

            # 啟動事件循環（非阻塞）
            app.processEvents()

            # 保持視窗運行（在背景執行事件循環）
            import threading
            def run_event_loop():
                try:
                    app.exec_()
                except Exception as e:
                    print(f"事件循環錯誤: {e}")

            event_thread = threading.Thread(target=run_event_loop)
            event_thread.daemon = False  # 改為非守護執行緒
            event_thread.start()

        except Exception as e:
            print(f"開啟滑鼠設定視窗時發生錯誤: {e}")
            import traceback
            traceback.print_exc()

    def hide_mouse_settings():
        nonlocal mouse_window
        if mouse_window is not None:
            mouse_window.hide()
            print("滑鼠設定視窗已隱藏")
        else:
            print("沒有滑鼠設定視窗可以隱藏")

    class MouseSettingsWindow(QMainWindow):
        def __init__(self, cross_coords):
            super().__init__()
            self.cross_coords = cross_coords
            self.initUI()

        def initUI(self):
            self.setWindowTitle('滑鼠動作設定')
            self.setGeometry(300, 300, 600, 400)

            # 創建中央 widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)

            # 創建佈局
            layout = QVBoxLayout(central_widget)

            # 創建表格
            self.table = QTableWidget(10, 6)  # 10 行，6 列
            self.table.setHorizontalHeaderLabels(['Enabled', '動作類型', 'X座標', 'Y座標', '延遲時間', '點擊類型'])

            # 設定表格屬性
            header = self.table.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.Stretch)

            # 設定預設值
            action_types = ['moveTo', 'click', 'dragTo']
            click_types = ['', 'left', 'right']

            for row in range(10):
                # Enabled checkbox
                enabled_checkbox = QCheckBox()
                if row == 0:  # 第一行預設為 true
                    enabled_checkbox.setChecked(True)
                else:  # 其他行預設為 false
                    enabled_checkbox.setChecked(False)
                self.table.setCellWidget(row, 0, enabled_checkbox)

                # 動作類型下拉選單
                action_combo = QComboBox()
                action_combo.addItems(action_types)
                if row == 0:  # 第一行預設為 moveTo
                    action_combo.setCurrentText('moveTo')
                self.table.setCellWidget(row, 1, action_combo)

                # X座標
                x_coord = ""
                if row == 0 and self.cross_coords:  # 第一行使用十字線座標
                    x_coord = str(self.cross_coords[-1][0])  # 使用最後一個座標
                x_item = QTableWidgetItem(x_coord)
                self.table.setItem(row, 2, x_item)

                # Y座標
                y_coord = ""
                if row == 0 and self.cross_coords:  # 第一行使用十字線座標
                    y_coord = str(self.cross_coords[-1][1])  # 使用最後一個座標
                y_item = QTableWidgetItem(y_coord)
                self.table.setItem(row, 3, y_item)

                # 延遲時間
                delay = "0.2"  # 預設 0.2s
                delay_item = QTableWidgetItem(delay)
                self.table.setItem(row, 4, delay_item)

                # 點擊類型下拉選單
                click_combo = QComboBox()
                click_combo.addItems(click_types)
                if row == 1:  # 第二行預設為 left
                    click_combo.setCurrentText('left')
                self.table.setCellWidget(row, 5, click_combo)

            layout.addWidget(self.table)

            # 創建按鈕佈局
            button_layout = QHBoxLayout()

            # 插入列按鈕
            insert_btn = QPushButton('插入列')
            insert_btn.clicked.connect(self.insert_row)
            button_layout.addWidget(insert_btn)

            # 刪除列按鈕
            delete_btn = QPushButton('刪除列')
            delete_btn.clicked.connect(self.delete_row)
            button_layout.addWidget(delete_btn)

            # 讀取座標位置按鈕
            load_coords_btn = QPushButton('讀取座標位置')
            load_coords_btn.clicked.connect(self.load_coordinates)
            button_layout.addWidget(load_coords_btn)

            # 執行按鈕
            execute_btn = QPushButton('執行動作')
            execute_btn.clicked.connect(self.execute_actions)
            button_layout.addWidget(execute_btn)

            # 清除按鈕
            clear_btn = QPushButton('清除')
            clear_btn.clicked.connect(self.clear_table)
            button_layout.addWidget(clear_btn)

            layout.addLayout(button_layout)

        def insert_row(self):
            current_row = self.table.currentRow()
            if current_row == -1:  # 如果沒有選中行，插入到最後
                current_row = self.table.rowCount() - 1

            self.table.insertRow(current_row + 1)

            # 為新行設定預設值
            self.setup_row_widgets(current_row + 1)

        def delete_row(self):
            current_row = self.table.currentRow()
            if current_row != -1:
                self.table.removeRow(current_row)

        def load_coordinates(self):
            current_row = self.table.currentRow()
            if current_row == -1:
                print("請先選擇一行")
                return

            print(f"讀取座標到第 {current_row + 1} 行...")

            # 從 cross_coords 中讀取座標並填入當前行
            coord_index = current_row % len(self.cross_coords) if self.cross_coords else 0
            if self.cross_coords and coord_index < len(self.cross_coords):
                x, y = self.cross_coords[coord_index]

                # 設定為啟用狀態
                enabled_checkbox = self.table.cellWidget(current_row, 0)
                if enabled_checkbox:
                    enabled_checkbox.setChecked(True)

                # 填入 X 座標
                x_item = QTableWidgetItem(str(x))
                self.table.setItem(current_row, 2, x_item)

                # 填入 Y 座標
                y_item = QTableWidgetItem(str(y))
                self.table.setItem(current_row, 3, y_item)

                print(f"已載入座標到第 {current_row + 1} 行: ({x}, {y})")
            else:
                print("沒有可用的座標")

        def setup_row_widgets(self, row):
            # Enabled checkbox
            enabled_checkbox = QCheckBox()
            enabled_checkbox.setChecked(False)
            self.table.setCellWidget(row, 0, enabled_checkbox)

            # 動作類型下拉選單
            action_combo = QComboBox()
            action_combo.addItems(['moveTo', 'click', 'dragTo'])
            self.table.setCellWidget(row, 1, action_combo)

            # X座標
            x_item = QTableWidgetItem("")
            self.table.setItem(row, 2, x_item)

            # Y座標
            y_item = QTableWidgetItem("")
            self.table.setItem(row, 3, y_item)

            # 延遲時間
            delay_item = QTableWidgetItem("0.2")
            self.table.setItem(row, 4, delay_item)

            # 點擊類型下拉選單
            click_combo = QComboBox()
            click_combo.addItems(['', 'left', 'right'])
            self.table.setCellWidget(row, 5, click_combo)

        def execute_actions(self):
            print("開始執行滑鼠動作...")
            for row in range(self.table.rowCount()):
                # 檢查是否啟用
                enabled_checkbox = self.table.cellWidget(row, 0)
                if not enabled_checkbox or not enabled_checkbox.isChecked():
                    continue

                action_type = self.table.cellWidget(row, 1).currentText()
                x_text = self.table.item(row, 2).text()
                y_text = self.table.item(row, 3).text()
                delay_text = self.table.item(row, 4).text()
                click_type = self.table.cellWidget(row, 5).currentText()

                # 檢查是否有有效的座標
                if not x_text or not y_text:
                    continue

                try:
                    x = int(x_text)
                    y = int(y_text)
                    delay = float(delay_text) if delay_text else 0.2

                    if action_type == 'moveTo':
                        pyautogui.moveTo(x, y, duration=delay)
                        print(f"移動到 ({x}, {y})")
                    elif action_type == 'click':
                        if click_type == 'left':
                            pyautogui.click(x, y)
                        elif click_type == 'right':
                            pyautogui.rightClick(x, y)
                        print(f"在 ({x}, {y}) 執行 {click_type} 點擊")
                    elif action_type == 'dragTo':
                        pyautogui.dragTo(x, y, duration=delay, button=click_type if click_type else 'left')
                        print(f"拖拽到 ({x}, {y})")

                    time.sleep(delay)

                except ValueError:
                    print(f"第 {row+1} 行座標格式錯誤，跳過")
                    continue

            print("滑鼠動作執行完成")

        def clear_table(self):
            for row in range(self.table.rowCount()):
                for col in range(self.table.columnCount()):
                    if col == 0:  # checkbox
                        self.table.cellWidget(row, col).setChecked(False)
                    elif col == 1 or col == 5:  # 下拉選單
                        self.table.cellWidget(row, col).setCurrentIndex(0)
                    else:  # 文字項目
                        self.table.setItem(row, col, QTableWidgetItem(""))

    def set_blue_cross():
        nonlocal cross_color
        cross_color = "blue"
        print("十字線顏色已設定為藍色")

    def refresh_screenshot():
        nonlocal full_screenshot, tk_img
        # 重新擷取螢幕
        full_screenshot = pyautogui.screenshot()
        tk_img = ImageTk.PhotoImage(full_screenshot)
        canvas.create_image(0, 0, anchor=tk.NW, image=tk_img)
        # 清除所有標記
        clear_rectangles()
        print("已重新擷取螢幕")

    def perform_ocr():
        if not point1 or not point2:
            print("需要先標記兩個點來定義 OCR 區域")
            return

        # 計算矩形區域
        x1, y1 = point1
        x2, y2 = point2
        left = min(x1, x2)
        top = min(y1, y2)
        right = max(x1, x2)
        bottom = max(y1, y2)
        width = right - left
        height = bottom - top

        # 從螢幕截圖中擷取區域
        region_img = full_screenshot.crop((left, top, right, bottom))

        try:
            # 進行 OCR 辨識
            text = pytesseract.image_to_string(region_img, lang='chi_tra+eng')  # 中文繁體 + 英文
            text = text.strip()

            if text:
                print(f"OCR 辨識結果:\n{text}")

                # 翻譯功能移至按鈕觸發，不在這裡自動翻譯
                translated_text = text

                # 顯示結果視窗
                result_window = tk.Toplevel(root)
                result_window.title("OCR 辨識結果")
                result_window.geometry("600x500")

                # 原始文字
                original_label = tk.Label(result_window, text="原始文字:", font=("Arial", 10, "bold"))
                original_label.pack(anchor=tk.W, padx=10, pady=(10,0))

                original_text_widget = tk.Text(result_window, wrap=tk.WORD, padx=10, pady=10, height=6)
                original_text_widget.insert(tk.END, text)
                original_text_widget.config(state=tk.DISABLED)
                original_text_widget.pack(fill=tk.X, padx=10)

                # 翻譯結果文字框（初始為空）
                translated_label = tk.Label(result_window, text="英文翻譯:", font=("Arial", 10, "bold"))
                translated_label.pack(anchor=tk.W, padx=10, pady=(10,0))

                translated_text_widget = tk.Text(result_window, wrap=tk.WORD, padx=10, pady=10, height=6)
                translated_text_widget.insert(tk.END, "")
                translated_text_widget.config(state=tk.DISABLED)
                translated_text_widget.pack(fill=tk.X, padx=10)

                # 按鈕區域
                button_frame = tk.Frame(result_window)
                button_frame.pack(fill=tk.X, padx=10, pady=10)

                # 複製原始文字按鈕
                def copy_original():
                    root.clipboard_clear()
                    root.clipboard_append(text)
                    print("已複製原始文字到剪貼簿")

                copy_original_btn = tk.Button(button_frame, text="複製原始文字", command=copy_original)
                copy_original_btn.pack(side=tk.LEFT, padx=(0,10))

                # 複製翻譯文字按鈕
                def copy_translated():
                    translated_content = translated_text_widget.get("1.0", tk.END).strip()
                    if translated_content:
                        root.clipboard_clear()
                        root.clipboard_append(translated_content)
                        print("已複製翻譯文字到剪貼簿")
                    else:
                        print("沒有翻譯內容可複製")

                copy_translated_btn = tk.Button(button_frame, text="複製英文翻譯", command=copy_translated)
                copy_translated_btn.pack(side=tk.LEFT, padx=(0,10))

                # 翻譯按鈕區域
                translate_frame = tk.Frame(result_window)
                translate_frame.pack(fill=tk.X, padx=10, pady=(0,10))

                def translate_to_english(from_lang="auto"):
                    if not TRANSLATION_AVAILABLE:
                        print("翻譯功能未安裝")
                        return

                    try:
                        print(f"正在翻譯文字 (來源語言: {from_lang})...")
                        if from_lang == "auto":
                            from translate import Translator as TranslateTranslator
                            specific_translator = TranslateTranslator(to_lang="en")
                            translation_result = specific_translator.translate(text)
                        else:
                            from translate import Translator as TranslateTranslator
                            specific_translator = TranslateTranslator(from_lang=from_lang, to_lang="en")
                            translation_result = specific_translator.translate(text)

                        # 更新翻譯文字框
                        translated_text_widget.config(state=tk.NORMAL)
                        translated_text_widget.delete("1.0", tk.END)
                        translated_text_widget.insert(tk.END, translation_result)
                        translated_text_widget.config(state=tk.DISABLED)

                        print(f"翻譯完成: {translation_result}")

                    except Exception as e:
                        print(f"翻譯失敗: {e}")
                        import traceback
                        traceback.print_exc()

                # 繁體中文翻譯按鈕
                if TRANSLATION_AVAILABLE:
                    traditional_btn = tk.Button(translate_frame, text="繁體中文翻英文",
                                              command=lambda: translate_to_english("zh-TW"))
                    traditional_btn.pack(side=tk.LEFT, padx=(0,10))

                    # 簡體中文翻譯按鈕
                    simplified_btn = tk.Button(translate_frame, text="簡體中文翻英文",
                                             command=lambda: translate_to_english("zh-CN"))
                    simplified_btn.pack(side=tk.LEFT, padx=(0,10))

                    # 自動檢測翻譯按鈕
                    auto_translate_btn = tk.Button(translate_frame, text="自動翻譯",
                                                 command=lambda: translate_to_english("auto"))
                    auto_translate_btn.pack(side=tk.LEFT)
                else:
                    no_translate_label = tk.Label(translate_frame, text="翻譯功能未安裝", fg="red")
                    no_translate_label.pack(side=tk.LEFT)
            else:
                print("OCR 未辨識到文字")

        except Exception as e:
            print(f"OCR 辨識失敗: {e}")

    canvas.bind("<Button-3>", show_context_menu)  # 右鍵綁定

    # 設定視窗大小為圖片大小
    root.geometry(f"{full_screenshot.width}x{full_screenshot.height}")
    root.resizable(False, False)
    root.attributes("-topmost", True)  # 確保視窗在最上層

    # 顯示視窗（非阻塞，等待用戶關閉）
    root.mainloop()

if __name__ == "__main__":
    screen_tools()