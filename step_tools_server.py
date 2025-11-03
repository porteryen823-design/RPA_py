import sys
import os
import grpc
from concurrent import futures
import threading
import socket
import sqlite3
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                              QHBoxLayout, QTableWidget, QTableWidgetItem,
                              QPushButton, QLineEdit, QLabel, QComboBox,
                              QInputDialog, QTextEdit, QDialog, QMessageBox,
                              QCheckBox, QHeaderView, QAbstractItemView,
                              QMenu, QAction, QShortcut, QListWidget)
from PyQt5.QtGui import (QTextCursor, QKeySequence, QTextCharFormat,
                         QColor, QFont, QIcon, QKeyEvent, QCloseEvent)
from PyQt5.QtCore import Qt, QTimer, QEvent
from typing import Optional, cast


# 添加 proto 路徑
sys.path.append(os.path.abspath('.'))

import proto.screen_tools_pb2 as screen_tools_pb2
import proto.screen_tools_pb2_grpc as screen_tools_pb2_grpc

# UI 設定檔案路徑
UI_SETTINGS_FILE = 'ui_settings.json'

class ScreenToolsServicer(screen_tools_pb2_grpc.ScreenToolsServiceServicer):
    def __init__(self, step_tools_app):
        self.step_tools_app = step_tools_app

    def add_step_to_datagrid(self, step_data):
        """在 UI datagrid 中添加步驟資料"""
        def update_ui():
            try:
                if not hasattr(self.step_tools_app, 'steps_table') or not self.step_tools_app.steps_table:
                    return
                    
                current_row_count = self.step_tools_app.steps_table.rowCount()
                self.step_tools_app.steps_table.insertRow(current_row_count)
                
                # 設置各個欄位
                self.step_tools_app.steps_table.setItem(current_row_count, 0, step_data['step_no'])
                self.step_tools_app.steps_table.setItem(current_row_count, 1, step_data['enabled'])
                self.step_tools_app.steps_table.setItem(current_row_count, 2, step_data['action_description'])
                self.step_tools_app.steps_table.setItem(current_row_count, 3, step_data['keyboard_action'])
                self.step_tools_app.steps_table.setItem(current_row_count, 4, step_data['mouse_action'])
                self.step_tools_app.steps_table.setItem(current_row_count, 5, step_data['coord_x'])
                self.step_tools_app.steps_table.setItem(current_row_count, 6, step_data['coord_y'])
                self.step_tools_app.steps_table.setItem(current_row_count, 7, step_data['duration'])
                self.step_tools_app.steps_table.setItem(current_row_count, 8, step_data['data'])
                self.step_tools_app.steps_table.setItem(current_row_count, 9, step_data['interval'])
                self.step_tools_app.steps_table.setItem(current_row_count, 10, step_data['delay_time'])
                self.step_tools_app.steps_table.setItem(current_row_count, 11, step_data['repeat_count'])
                
            except Exception as e:
                print(f"Error updating UI: {e}")
        
        # 在 UI 執行緒中更新
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(0, update_ui)

    def create_step_data_for_mouse_action(self, step_no, request, project_id):
        """為滑鼠動作創建步驟資料"""
        from PyQt5.QtWidgets import QTableWidgetItem
        
        # 根據 action_type 設置動作描述和相關參數
        if request.action_type == "moveTo":
            action_description = "moveTo"
            mouse_action = True
            keyboard_action = False
        elif request.action_type == "click":
            action_description = "click"
            if hasattr(request, 'button') and request.button == "right":
                action_description = "rightClick"
            mouse_action = True
            keyboard_action = False
        elif request.action_type == "dragTo":
            action_description = "dragTo"
            if hasattr(request, 'button') and request.button == "right":
                action_description = "rightDrag"
            mouse_action = True
            keyboard_action = False
        else:
            action_description = request.action_type
            mouse_action = True
            keyboard_action = False
        
        # 獲取參數
        x, y = request.x, request.y
        duration = request.duration if request.duration > 0 else 0.1
        interval = getattr(request, 'interval', 0.1)
        delay_time = getattr(request, 'delay_time', 0.1)
        
        return {
            'step_no': QTableWidgetItem(str(step_no)),
            'enabled': self.create_checkbox_item(True),
            'action_description': QTableWidgetItem(action_description),
            'keyboard_action': self.create_checkbox_item(keyboard_action),
            'mouse_action': self.create_checkbox_item(mouse_action),
            'coord_x': QTableWidgetItem(str(x) if x is not None else ''),
            'coord_y': QTableWidgetItem(str(y) if y is not None else ''),
            'duration': QTableWidgetItem(str(duration)),
            'data': QTableWidgetItem(''),
            'interval': QTableWidgetItem(str(interval)),
            'delay_time': QTableWidgetItem(str(delay_time)),
            'repeat_count': QTableWidgetItem('1')
        }

    def create_step_data_for_keyboard_action(self, step_no, request, project_id):
        """為鍵盤動作創建步驟資料"""
        from PyQt5.QtWidgets import QTableWidgetItem
        
        action_type = request.action_type
        if action_type == "press":
            key = getattr(request, 'key', '')
            action_description = f"press({key})" if key else "press"
        elif action_type == "hotkey":
            keys = list(request.keys) if hasattr(request, 'keys') else []
            action_description = f"hotkey({','.join([repr(k) for k in keys])})" if keys else "hotkey"
        elif action_type == "write":
            text = getattr(request, 'text', '')
            action_description = "write"
        else:
            action_description = action_type
        
        duration = request.duration if request.duration > 0 else 0.1
        interval = getattr(request, 'interval', 0.1)
        delay_time = getattr(request, 'delay_time', 0.1)
        
        data_value = ''
        if action_type == "press":
            data_value = getattr(request, 'key', '')
        elif action_type == "hotkey":
            keys = list(request.keys) if hasattr(request, 'keys') else []
            data_value = ','.join(keys)
        elif action_type == "write":
            data_value = getattr(request, 'text', '')
        
        return {
            'step_no': QTableWidgetItem(str(step_no)),
            'enabled': self.create_checkbox_item(True),
            'action_description': QTableWidgetItem(action_description),
            'keyboard_action': self.create_checkbox_item(True),
            'mouse_action': self.create_checkbox_item(False),
            'coord_x': QTableWidgetItem(''),
            'coord_y': QTableWidgetItem(''),
            'duration': QTableWidgetItem(str(duration)),
            'data': QTableWidgetItem(data_value),
            'interval': QTableWidgetItem(str(interval)),
            'delay_time': QTableWidgetItem(str(delay_time)),
            'repeat_count': QTableWidgetItem('1')
        }

    def create_checkbox_item(self, checked):
        """創建勾選框項目"""
        from PyQt5.QtWidgets import QTableWidgetItem
        from PyQt5.QtCore import Qt
        
        item = QTableWidgetItem()
        item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        item.setCheckState(Qt.Checked if checked else Qt.Unchecked)
        return item

    def TakeScreenshot(self, request, context):
        """處理螢幕截圖請求"""
        try:
            import pyautogui
            from PIL import Image
            import io

            if request.region == "full":
                screenshot = pyautogui.screenshot()
            else:
                # 解析區域座標 x1,y1,x2,y2
                coords = request.region.split(',')
                if len(coords) == 4:
                    x1, y1, x2, y2 = map(int, coords)
                    screenshot = pyautogui.screenshot(region=(x1, y1, x2-x1, y2-y1))
                else:
                    screenshot = pyautogui.screenshot()

            # 轉換為 bytes
            img_byte_arr = io.BytesIO()
            screenshot.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()

            return screen_tools_pb2.ScreenshotResponse(
                image_data=img_bytes,
                width=screenshot.width,
                height=screenshot.height,
                timestamp="current"
            )
        except Exception as e:
            context.set_details(f'Screenshot failed: {str(e)}')
            context.set_code(grpc.StatusCode.INTERNAL)
            return screen_tools_pb2.ScreenshotResponse()

    def SaveScreenshot(self, request, context):
        """處理儲存螢幕截圖請求"""
        try:
            from PIL import Image
            import io
            import datetime
            import os

            # 從 bytes 創建圖片
            image = Image.open(io.BytesIO(request.image_data))

            # 確保目錄存在
            os.makedirs(request.path, exist_ok=True)

            # 儲存圖片
            full_path = os.path.join(request.path, request.filename)
            image.save(full_path)

            return screen_tools_pb2.SaveResponse(
                success=True,
                message="Screenshot saved successfully",
                saved_path=full_path
            )
        except Exception as e:
            return screen_tools_pb2.SaveResponse(
                success=False,
                message=f'Failed to save screenshot: {str(e)}'
            )

    def ExecuteMouseAction(self, request, context):
        """處理滑鼠動作請求 - 改為在 datagrid 中添加資料"""
        try:
            # 獲取當前專案ID
            if not hasattr(self.step_tools_app, 'current_project_id') or not self.step_tools_app.current_project_id:
                return screen_tools_pb2.ActionResponse(
                    success=False,
                    message="No current project selected"
                )

            current_project_id = self.step_tools_app.current_project_id
            
            # 獲取最後一個步驟編號，用於生成新的步驟編號
            # 直接在 UI 計算下一步驟編號，不修改資料庫
            current_row_count = self.step_tools_app.steps_table.rowCount()
            if current_row_count > 0:
                # 獲取最後一行的步驟編號
                last_row_step_no = int(self.step_tools_app.steps_table.item(current_row_count - 1, 0).text())
                next_step_no = last_row_step_no + 10
            else:
                next_step_no = 10

            # 創建步驟資料並添加到 datagrid
            step_data = self.create_step_data_for_mouse_action(
                next_step_no, request, current_project_id
            )
            
            # 在 datagrid 中添加資料
            self.add_step_to_datagrid(step_data)
            
            # 在 listbox 中顯示訊息
            try:
                if hasattr(self.step_tools_app, 'add_message_to_list'):
                    from PyQt5.QtCore import QTimer
                    message = f"收到滑鼠動作: {request.action_type} at ({request.x}, {request.y})"
                    QTimer.singleShot(0, lambda: self.step_tools_app.add_message_to_list(message))
            except Exception as e:
                print(f"Warning: Could not update message list: {e}")
            # 在 datagrid 中添加資料
            self.add_step_to_datagrid(step_data)
            
            return screen_tools_pb2.ActionResponse(
                success=True,
                message=f"Mouse action '{request.action_type}' added to datagrid successfully"
            )
        except Exception as e:
            return screen_tools_pb2.ActionResponse(
                success=False,
                message=f'Failed to add mouse action to datagrid: {str(e)}'
            )

    def ExecuteKeyboardAction(self, request, context):
        """處理鍵盤動作請求 - 改為在 datagrid 中添加資料"""
        try:
            # 獲取當前專案ID
            if not hasattr(self.step_tools_app, 'current_project_id') or not self.step_tools_app.current_project_id:
                return screen_tools_pb2.ActionResponse(
                    success=False,
                    message="No current project selected"
                )

            current_project_id = self.step_tools_app.current_project_id
            
            # 獲取最後一個步驟編號，用於生成新的步驟編號
            # 直接在 UI 計算下一步驟編號，不修改資料庫
            current_row_count = self.step_tools_app.steps_table.rowCount()
            if current_row_count > 0:
                # 獲取最後一行的步驟編號
                last_row_step_no = int(self.step_tools_app.steps_table.item(current_row_count - 1, 0).text())
                next_step_no = last_row_step_no + 10
            else:
                next_step_no = 10

            # 創建步驟資料並添加到 datagrid
            step_data = self.create_step_data_for_keyboard_action(
                next_step_no, request, current_project_id
            )
            
            # 在 datagrid 中添加資料
            self.add_step_to_datagrid(step_data)
            
            # 在 listbox 中顯示訊息
            try:
                if hasattr(self.step_tools_app, 'add_message_to_list'):
                    from PyQt5.QtCore import QTimer
                    key_info = getattr(request, 'key', '') or getattr(request, 'text', '') or str(list(request.keys) if hasattr(request, 'keys') else [])
                    message = f"收到鍵盤動作: {request.action_type} {key_info}"
                    QTimer.singleShot(0, lambda: self.step_tools_app.add_message_to_list(message))
                    
                    # 新增這一行以顯示在 message_list
                    QTimer.singleShot(0, lambda: self.step_tools_app.add_message_to_list(f"SyncScreenData: Step added to datagrid successfully: 鍵盤 {key_info}"))
            except Exception as e:
                print(f"Warning: Could not update message list: {e}")
                
            # 在 datagrid 中添加資料
            self.add_step_to_datagrid(step_data)
            
            return screen_tools_pb2.ActionResponse(
                success=True,
                message=f"Keyboard action '{request.action_type}' added to datagrid successfully"
            )
        except Exception as e:
            return screen_tools_pb2.ActionResponse(
                success=False,
                message=f'Failed to add keyboard action to datagrid: {str(e)}'
            )

    def PerformOCR(self, request, context):
        """處理 OCR 請求"""
        try:
            from PIL import Image
            import io

            # 檢查 OCR 是否可用
            try:
                import pytesseract
                pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            except ImportError:
                return screen_tools_pb2.OCRResponse(
                    text="",
                    confidence=0.0,
                    language="error: pytesseract not installed"
                )

            # 從 bytes 創建圖片
            image = Image.open(io.BytesIO(request.image_data))

            # 如果指定區域，裁切圖片
            if request.region:
                coords = request.region.split(',')
                if len(coords) == 4:
                    x1, y1, x2, y2 = map(int, coords)
                    image = image.crop((x1, y1, x2, y2))

            # 進行 OCR
            lang = request.language if request.language else 'chi_tra+eng'
            text = pytesseract.image_to_string(image, lang=lang)

            return screen_tools_pb2.OCRResponse(
                text=text.strip(),
                confidence=0.8,  # 簡化版，不計算實際信心度
                language=lang
            )
        except Exception as e:
            return screen_tools_pb2.OCRResponse(
                text="",
                confidence=0.0,
                language=f"error: {str(e)}"
            )

    def SaveCoordinates(self, request, context):
        """處理儲存座標請求"""
        try:
            # 這裡可以將座標儲存到 Step_Tools 的資料庫中
            # 簡化版：只返回成功
            coords_list = []
            for coord in request.coordinates:
                coords_list.append(f"({coord.x}, {coord.y}) - {coord.label}")

            return screen_tools_pb2.SaveResponse(
                success=True,
                message=f"Coordinates saved: {', '.join(coords_list)}"
            )
        except Exception as e:
            return screen_tools_pb2.SaveResponse(
                success=False,
                message=f'Failed to save coordinates: {str(e)}'
            )

    def GetCoordinates(self, request, context):
        """處理獲取座標請求"""
        try:
            # 簡化版：返回空的座標列表
            return screen_tools_pb2.CoordinatesResponse(coordinates=[])
        except Exception as e:
            context.set_details(f'Failed to get coordinates: {str(e)}')
            context.set_code(grpc.StatusCode.INTERNAL)
            return screen_tools_pb2.CoordinatesResponse()

    def SyncScreenData(self, request, context):
        """處理螢幕資料同步請求 - 改為在 datagrid 中添加資料"""
        try:
            response_msg = "Screen data synced successfully"

            if request.data_type == "add_step" and request.coordinates:
                # 添加新步驟到 datagrid - 不直接修改資料庫
                try:
                    # 添加新步驟到 datagrid
                    coord = request.coordinates[0]  # 使用第一個座標
                    x, y = coord.x, coord.y
                    action_label = coord.label

                    # 根據標籤判斷動作類型
                    if action_label.startswith("mouse_"):
                        action_type = action_label.replace("mouse_", "")
                        mouse_action = True
                        keyboard_action = False
                        action_description = f"滑鼠{action_type}"
                    elif action_label.startswith("keyboard_"):
                        action_type = action_label.replace("keyboard_", "")
                        mouse_action = False
                        keyboard_action = True
                        action_description = f"鍵盤{action_type}"
                    else:
                        mouse_action = False
                        keyboard_action = False
                        action_description = "未知動作"

                    # 獲取下一步驟編號
                    current_row_count = self.step_tools_app.steps_table.rowCount()
                    if current_row_count > 0:
                        # 獲取最後一行的步驟編號
                        last_row_step_no = int(self.step_tools_app.steps_table.item(current_row_count - 1, 0).text())
                        next_step_no = last_row_step_no + 10
                    else:
                        next_step_no = 10

                    # 創建步驟資料
                    from PyQt5.QtWidgets import QTableWidgetItem
                    step_data = {
                        'step_no': QTableWidgetItem(str(next_step_no)),
                        'enabled': self.create_checkbox_item(True),
                        'action_description': QTableWidgetItem(action_description),
                        'keyboard_action': self.create_checkbox_item(keyboard_action),
                        'mouse_action': self.create_checkbox_item(mouse_action),
                        'coord_x': QTableWidgetItem(str(x) if x is not None else ''),
                        'coord_y': QTableWidgetItem(str(y) if y is not None else ''),
                        'duration': QTableWidgetItem('0.2'),
                        'data': QTableWidgetItem(''),
                        'interval': QTableWidgetItem('0.2'),
                        'delay_time': QTableWidgetItem('0.2'),
                        'repeat_count': QTableWidgetItem('1')
                    }
                    
                    # 在 datagrid 中添加資料
                    self.add_step_to_datagrid(step_data)
                    
                    response_msg = f"Step added to datagrid successfully: {action_description} at ({x}, {y})"

                except Exception as e:
                    response_msg = f"Failed to add step to datagrid: {str(e)}"

            elif request.data_type == "screenshot" and request.image_data:
                response_msg += " - Screenshot received"
            elif request.coordinates:
                coords_count = len(request.coordinates)
                response_msg += f" - {coords_count} coordinates received"
            if request.mouse_position:
                response_msg += f" - Mouse position: ({request.mouse_position.x}, {request.mouse_position.y})"

            # 寫入 console
            print(f"[gRPC] SyncScreenData: {response_msg}")

            # 在畫面 ListBox 顯示訊息（使用執行緒安全的方式）
            try:
                if hasattr(self.step_tools_app, 'add_message_to_list'):
                    # 使用 QTimer 在 UI 執行緒中更新訊息
                    from PyQt5.QtCore import QTimer
                    QTimer.singleShot(0, lambda: self.step_tools_app.add_message_to_list(f"SyncScreenData: {response_msg}"))
            except Exception as e:
                print(f"Warning: Could not update message list: {e}")

            return screen_tools_pb2.SyncResponse(
                success=True,
                message=response_msg,
                server_status="active"
            )
        except Exception as e:
            error_msg = f'Failed to sync screen data: {str(e)}'
            print(f"[gRPC] SyncScreenData Error: {error_msg}")
            try:
                if hasattr(self.step_tools_app, 'add_message_to_list'):
                    from PyQt5.QtCore import QTimer
                    QTimer.singleShot(0, lambda: self.step_tools_app.add_message_to_list(f"SyncScreenData Error: {error_msg}"))
            except:
                pass
            return screen_tools_pb2.SyncResponse(
                success=False,
                message=error_msg,
                server_status="error"
            )


class StepToolsApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.load_ui_settings()
        self.init_database()
        self.init_ui()
        self.load_projects()

        # 用於跟踪用戶是否已經選取行
        self.user_selected_row = False  # 初始化 user_selected_row

        # 啟動 gRPC server
        self.start_grpc_server()

    def start_grpc_server(self):
        """啟動 gRPC server"""
        def serve():
            server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
            screen_tools_pb2_grpc.add_ScreenToolsServiceServicer_to_server(
                ScreenToolsServicer(self), server)
            server.add_insecure_port('[::]:50052')  # 使用不同的端口
            server.start()
            print("gRPC Server started on port 50052")
            server.wait_for_termination()

        server_thread = threading.Thread(target=serve)
        server_thread.daemon = True
        server_thread.start()

    def init_database(self) -> bool:
        """初始化資料庫"""
        try:
            self.db_connection = sqlite3.connect('step_tools.db')
            if not self.db_connection:
                QMessageBox.critical(self, "Database Error", "無法建立資料庫連接")
                return False

            # 檢查資料庫連接是否有效
            try:
                cursor = self.db_connection.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                cursor.close()
                return True
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"資料庫測試失敗: {str(e)}")
                self.db_connection.close()
                self.db_connection = None
                return False

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"資料庫連接失敗: {str(e)}")
            self.db_connection = None
            return False

        # 建立專案表格
        cursor = self.db_connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                project_id TEXT PRIMARY KEY,
                project_name TEXT NOT NULL,
                create_date TEXT NOT NULL,
                create_user TEXT NOT NULL
            )
        ''')

        # 建立步驟表格
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                step_no INTEGER NOT NULL,
                enabled BOOLEAN NOT NULL DEFAULT 1,
                action_description TEXT,
                keyboard_action BOOLEAN NOT NULL DEFAULT 0,
                mouse_action BOOLEAN NOT NULL DEFAULT 0,
                coord_x INTEGER,
                coord_y INTEGER,
                duration REAL DEFAULT 0.0,
                data TEXT,
                interval REAL DEFAULT 0.0,
                delay_time REAL DEFAULT 0.0,
                repeat_count INTEGER DEFAULT 1,
                FOREIGN KEY (project_id) REFERENCES projects (project_id),
                UNIQUE(project_id, step_no)
            )
        ''')

        self.db_connection.commit()

    def load_ui_settings(self):
        """載入 UI 設定"""
        try:
            if os.path.exists(UI_SETTINGS_FILE):
                with open(UI_SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    self.ui_settings = json.load(f)
            else:
                self.ui_settings = {}
        except Exception as e:
            print(f"載入 UI 設定失敗: {str(e)}")
            self.ui_settings = {}

    def save_ui_settings(self):
        """儲存 UI 設定"""
        try:
            # 儲存欄位寬度
            if hasattr(self, 'steps_table') and self.steps_table:
                column_widths = {}
                header = self.steps_table.horizontalHeader()
                if header:
                    for col in range(self.steps_table.columnCount()):
                        width = header.sectionSize(col)
                        column_widths[str(col)] = width
                self.ui_settings['column_widths'] = column_widths
            
            with open(UI_SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.ui_settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"儲存 UI 設定失敗: {str(e)}")

    def init_ui(self):
        """初始化使用者介面"""
        self.setWindowTitle('步驟工具管理系統 (gRPC Server)')
        self.setGeometry(100, 100, 1200, 800)

        # 建立中央 widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主佈局
        main_layout = QVBoxLayout(central_widget)

        # 新增 Label 來顯示目前選取的行
        self.selected_row_label = QLabel("目前選取行: None")
        self.selected_row_label.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(self.selected_row_label)  # 將 Label 添加到主佈局

        # 專案區域
        project_layout = QHBoxLayout()
        project_label = QLabel('專案：')
        self.project_combo = QComboBox()
        self.project_combo.currentTextChanged.connect(self.on_project_changed)
        create_project_btn = QPushButton('建立新專案')
        create_project_btn.clicked.connect(self.create_new_project)
        copy_project_btn = QPushButton('複製專案')
        copy_project_btn.clicked.connect(self.copy_current_project)

        project_layout.addWidget(project_label)
        project_layout.addWidget(self.project_combo)
        project_layout.addWidget(create_project_btn)
        project_layout.addWidget(copy_project_btn)
        project_layout.addStretch()

        main_layout.addLayout(project_layout)

        # 設定步驟表格
        self.steps_table = QTableWidget()
        self.setup_steps_table()
        main_layout.addWidget(self.steps_table)

        # 連接 itemClicked 信號
        self.steps_table.itemClicked.connect(self.update_selected_row_label)

        # 按鈕區域
        button_layout = QHBoxLayout()

        add_above_btn = QPushButton('在上方新增步驟')
        add_above_btn.clicked.connect(lambda: self.add_step_at_position('above'))
        button_layout.addWidget(add_above_btn)

        add_below_btn = QPushButton('在下方新增步驟')
        add_below_btn.clicked.connect(lambda: self.add_step_at_position('below'))
        button_layout.addWidget(add_below_btn)

        add_step_btn = QPushButton('新增步驟')
        add_step_btn.clicked.connect(self.add_step)
        button_layout.addWidget(add_step_btn)

        delete_step_btn = QPushButton('刪除步驟')
        delete_step_btn.clicked.connect(self.delete_step)
        button_layout.addWidget(delete_step_btn)

        # 批次啟用/停用按鈕
        enable_above_btn = QPushButton('以上全部啟用')
        enable_above_btn.clicked.connect(lambda: self.batch_enable_disable('above', True))
        button_layout.addWidget(enable_above_btn)

        disable_above_btn = QPushButton('以上全部停用')
        disable_above_btn.clicked.connect(lambda: self.batch_enable_disable('above', False))
        button_layout.addWidget(disable_above_btn)

        enable_below_btn = QPushButton('以下全部啟用')
        enable_below_btn.clicked.connect(lambda: self.batch_enable_disable('below', True))
        button_layout.addWidget(enable_below_btn)

        disable_below_btn = QPushButton('以下全部停用')
        disable_below_btn.clicked.connect(lambda: self.batch_enable_disable('below', False))
        button_layout.addWidget(disable_below_btn)

        renumber_btn = QPushButton('重新編號')
        renumber_btn.clicked.connect(self.renumber_steps)
        button_layout.addWidget(renumber_btn)

        save_btn = QPushButton('儲存')
        save_btn.clicked.connect(self.save_data)
        button_layout.addWidget(save_btn)

        run_btn = QPushButton('執行')
        run_btn.clicked.connect(self.run_steps)
        button_layout.addWidget(run_btn)

        button_layout.addStretch()

        main_layout.addLayout(button_layout)
        # gRPC 訊息列表
        self.message_list = QListWidget()
        self.message_list.setMaximumHeight(150)
        main_layout.addWidget(QLabel("gRPC 訊息:"))
        main_layout.addWidget(self.message_list)

    def add_message_to_list(self, message):
        """添加訊息到列表"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}"
        self.message_list.addItem(full_message)
        if self.message_list.count() > 10:
            self.message_list.takeItem(0)  

    def setup_steps_table(self):
        """設定步驟表格"""
        headers = ['步驟編號', '啟用', '動作說明', '鍵盤動作', '滑鼠動作',
                   '座標 X', '座標 Y', '持續時間', '資料', '間隔', '延遲時間', '重複次數']
        self.steps_table.setColumnCount(len(headers))
        self.steps_table.setHorizontalHeaderLabels(headers)

        # 設定欄位寬度和調整行為
        if self.steps_table and self.steps_table.horizontalHeader():
            header = self.steps_table.horizontalHeader()
            if header:
                header.setSectionResizeMode(QHeaderView.Interactive)  # 允許手動調整寬度
                header.setSectionsMovable(True)  # 允許拖動調整欄位順序
                header.setStretchLastSection(True)  # 最後一欄自動拉伸

                # 設定預設欄位寬度
                header.resizeSection(0, 100)   # 步驟編號
                header.resizeSection(1, 60)    # 啟用
                header.resizeSection(2, 200)   # 動作說明
                header.resizeSection(3, 80)    # 鍵盤動作
                header.resizeSection(4, 80)    # 滑鼠動作
                header.resizeSection(5, 70)    # 座標 X
                header.resizeSection(6, 70)    # 座標 Y
                header.resizeSection(7, 80)    # 持續時間
                header.resizeSection(8, 150)   # 資料
                header.resizeSection(9, 70)    # 間隔
                header.resizeSection(10, 80)   # 延遲時間
                header.resizeSection(11, 80)   # 重複次數

        self.steps_table.setAlternatingRowColors(True)
        self.steps_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # 設定右鍵選單
        self.steps_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.steps_table.customContextMenuRequested.connect(self.show_context_menu)

    def load_projects(self):
        """載入專案列表"""
        if not self.db_connection and not self.init_database():
            return

        try:
            if not self.db_connection:
                raise Exception("Database not connected")

            cursor = self.db_connection.cursor()
            cursor.execute('SELECT project_name FROM projects ORDER BY create_date DESC')
            projects = cursor.fetchall()

            self.project_combo.clear()
            for project in projects:
                if project and project[0]:
                    self.project_combo.addItem(project[0])

            # 如果有專案，載入第一個
            if projects and projects[0] and projects[0][0]:
                self.load_project_steps(projects[0][0])
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"載入專案失敗: {str(e)}")

    def on_project_changed(self, project_name):
        """專案變更事件"""
        if project_name:
            self.load_project_steps(project_name)

    def load_project_steps(self, project_name):
        """載入專案步驟"""
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT project_id FROM projects WHERE project_name = ?', (project_name,))
        result = cursor.fetchone()
        if result:
            self.current_project_id = result[0]
            self.load_steps()

    def load_steps(self):
        """載入步驟資料"""
        if not self.current_project_id:
            return

        cursor = self.db_connection.cursor()
        cursor.execute('''
            SELECT step_no, enabled, action_description, keyboard_action, mouse_action,
                   coord_x, coord_y, duration, data, interval, delay_time, repeat_count
            FROM steps
            WHERE project_id = ?
            ORDER BY step_no
        ''', (self.current_project_id,))

        steps = cursor.fetchall()
        self.steps_table.setRowCount(len(steps))

        for row, step in enumerate(steps):
            # 步驟編號 (唯讀)
            step_no = str(step[0]) if step and step[0] is not None else ""
            step_no_item = QTableWidgetItem(step_no)
            if step_no_item:
                step_no_item.setFlags(step_no_item.flags() & ~Qt.ItemIsEditable)
                self.steps_table.setItem(row, 0, step_no_item)

            # 啟用勾選框
            enabled_item = QTableWidgetItem()
            if enabled_item:
                enabled_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                enabled_item.setCheckState(Qt.Checked if step and step[1] else Qt.Unchecked)
                self.steps_table.setItem(row, 1, enabled_item)

            # 動作說明
            action_desc_item = QTableWidgetItem(str(step[2]) if step[2] else '')
            self.steps_table.setItem(row, 2, action_desc_item)

            # 鍵盤動作勾選框
            keyboard_item = QTableWidgetItem()
            keyboard_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            keyboard_item.setCheckState(Qt.Checked if step[3] else Qt.Unchecked)
            self.steps_table.setItem(row, 3, keyboard_item)

            # 滑鼠動作勾選框
            mouse_item = QTableWidgetItem()
            mouse_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            mouse_item.setCheckState(Qt.Checked if step[4] else Qt.Unchecked)
            self.steps_table.setItem(row, 4, mouse_item)

            # 其他欄位
            for col in range(5, len(step)):
                value = step[col]
                self.steps_table.setItem(row, col, QTableWidgetItem(str(value) if value is not None else ''))

    def update_selected_row_label(self, item):
        """更新目前選取行的 Label"""
        if item:
            row = item.row()
            self.selected_row_label.setText(f"目前選取行: {row + 1}")  # +1 使行數從 1 開始
            self.user_selected_row = True  # 標記用戶已選取行
        else:
            self.selected_row_label.setText("目前選取行: None")

    def create_new_project(self):
        """建立新專案"""
        dialog = CreateProjectDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            project_name = dialog.project_name_edit.text().strip()
            if project_name:
                self.create_project(project_name)

    def copy_current_project(self):
        """複製目前專案"""
        current_project_name = self.project_combo.currentText()
        if not current_project_name:
            QMessageBox.warning(self, '警告', '請先選擇要複製的專案')
            return

        dialog = CopyProjectDialog(current_project_name, self)
        if dialog.exec_() == QDialog.Accepted:
            new_project_name = dialog.new_project_name_edit.text().strip()
            if new_project_name:
                self.copy_project_from_name(current_project_name, new_project_name)

    def create_project(self, project_name):
        """建立專案"""
        import uuid
        project_id = str(uuid.uuid4())

        cursor = self.db_connection.cursor()
        cursor.execute('''
            INSERT INTO projects (project_id, project_name, create_date, create_user)
            VALUES (?, ?, datetime('now'), 'user')
        ''', (project_id, project_name))

        # 建立預設步驟
        for i in range(1, 101):  # 10, 20, 30, ..., 1000
            step_no = i * 10
            cursor.execute('''
                INSERT INTO steps (project_id, step_no, enabled, action_description)
                VALUES (?, ?, 1, '')
            ''', (project_id, step_no))

        self.db_connection.commit()
        self.load_projects()

    def add_step(self):
        """新增步驟"""
        if not self.current_project_id:
            QMessageBox.warning(self, '警告', '請先選擇專案')
            return

        # 找到最後一個步驟編號
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT MAX(step_no) FROM steps WHERE project_id = ?', (self.current_project_id,))
        result = cursor.fetchone()
        next_step_no = (result[0] or 0) + 10

        cursor.execute('''
            INSERT INTO steps (project_id, step_no, enabled, action_description)
            VALUES (?, ?, 1, '新步驟')
        ''', (self.current_project_id, next_step_no))

        self.db_connection.commit()
        self.load_steps()

    def delete_step(self):
        """刪除步驟"""
        current_row = self.steps_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, '警告', '請選擇要刪除的步驟')
            return

        step_no = int(self.steps_table.item(current_row, 0).text())

        cursor = self.db_connection.cursor()

        # 刪除步驟
        cursor.execute('DELETE FROM steps WHERE project_id = ? AND step_no = ?',
                      (self.current_project_id, step_no))

        # 重新編號剩餘步驟（避免 UNIQUE 約束衝突）
        # 先將所有步驟編號設為負數
        cursor.execute('UPDATE steps SET step_no = -ABS(step_no) WHERE project_id = ?',
                      (self.current_project_id,))

        # 重新編號為 10, 20, 30... 按照原順序
        cursor.execute('''
            SELECT id FROM steps
            WHERE project_id = ?
            ORDER BY step_no DESC
        ''', (self.current_project_id,))

        step_ids = cursor.fetchall()
        for i, (step_id,) in enumerate(step_ids):
            new_step_no = (i + 1) * 10
            cursor.execute('UPDATE steps SET step_no = ? WHERE id = ?', (new_step_no, step_id))

        self.db_connection.commit()

        # 重新載入步驟並調整選擇位置
        self.load_steps()

        # 調整選擇位置，避免超出範圍
        row_count = self.steps_table.rowCount()
        if row_count > 0:
            # 如果刪除的是最後一行，選擇前一行，否則選擇同一位置
            new_row = min(current_row, row_count - 1)
            self.steps_table.selectRow(new_row)

    def renumber_steps(self):
        """重新編號步驟"""
        if not self.current_project_id:
            return

        cursor = self.db_connection.cursor()

        # 先將所有步驟編號設為負數，避免 UNIQUE 約束衝突
        cursor.execute('''
            UPDATE steps SET step_no = -step_no
            WHERE project_id = ?
        ''', (self.current_project_id,))

        # 重新編號為 10, 20, 30... 按照 step_no 順序
        cursor.execute('''
            SELECT id FROM steps
            WHERE project_id = ?
            ORDER BY step_no DESC
        ''', (self.current_project_id,))

        step_ids = cursor.fetchall()
        for i, (step_id,) in enumerate(step_ids):
            new_step_no = (i + 1) * 10
            cursor.execute('UPDATE steps SET step_no = ? WHERE id = ?', (new_step_no, step_id))

        self.db_connection.commit()
        self.load_steps()

    def save_data(self):
        """儲存資料"""
        if not self.current_project_id:
            QMessageBox.warning(self, '警告', '請先選擇專案')
            return

        cursor = self.db_connection.cursor()

        for row in range(self.steps_table.rowCount()):
            step_no = int(self.steps_table.item(row, 0).text())
            enabled = self.steps_table.item(row, 1).checkState() == Qt.Checked
            action_description = self.steps_table.item(row, 2).text() if self.steps_table.item(row, 2) else ''
            keyboard_action = self.steps_table.item(row, 3).checkState() == Qt.Checked if self.steps_table.item(row, 3) else False
            mouse_action = self.steps_table.item(row, 4).checkState() == Qt.Checked if self.steps_table.item(row, 4) else False
            coord_x = int(self.steps_table.item(row, 5).text()) if self.steps_table.item(row, 5) and self.steps_table.item(row, 5).text() else None
            coord_y = int(self.steps_table.item(row, 6).text()) if self.steps_table.item(row, 6) and self.steps_table.item(row, 6).text() else None
            duration = float(self.steps_table.item(row, 7).text()) if self.steps_table.item(row, 7) and self.steps_table.item(row, 7).text() else 0.0
            data = self.steps_table.item(row, 8).text() if self.steps_table.item(row, 8) else ''
            interval = float(self.steps_table.item(row, 9).text()) if self.steps_table.item(row, 9) and self.steps_table.item(row, 9).text() else 0.0
            delay_time = float(self.steps_table.item(row, 10).text()) if self.steps_table.item(row, 10) and self.steps_table.item(row, 10).text() else 0.0
            repeat_count = int(self.steps_table.item(row, 11).text()) if self.steps_table.item(row, 11) and self.steps_table.item(row, 11).text() else 1

            cursor.execute('''
                UPDATE steps SET
                    enabled = ?, action_description = ?, keyboard_action = ?, mouse_action = ?,
                    coord_x = ?, coord_y = ?, duration = ?, data = ?, interval = ?,
                    delay_time = ?, repeat_count = ?
                where project_id = ? and step_no = ?
            ''', (enabled, action_description, keyboard_action, mouse_action,
                  coord_x, coord_y, duration, data, interval, delay_time, repeat_count,
                  self.current_project_id, step_no))

        self.db_connection.commit()
        QMessageBox.information(self, '成功', '資料已儲存')

    def run_steps(self):
        """執行步驟"""
        if not self.current_project_id:
            QMessageBox.warning(self, '警告', '請先選擇專案')
            return

        cursor = self.db_connection.cursor()
        cursor.execute('''
            SELECT step_no, enabled, action_description, keyboard_action, mouse_action,
                   coord_x, coord_y, duration, data, interval, delay_time, repeat_count
            FROM steps
            where project_id = ? and enabled = 1
            ORDER BY step_no
        ''', (self.current_project_id,))

        steps = cursor.fetchall()
        if not steps:
            QMessageBox.warning(self, '警告', '沒有啟用的步驟')
            return

        # 顯示執行確認對話框
        dialog = RunStepsDialog(steps, self)
        dialog.exec_()

    def add_step_at_position(self, position):
        """在指定位置新增步驟"""
        current_row = self.steps_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, '警告', '請選擇步驟')
            return

        current_step_no = int(self.steps_table.item(current_row, 0).text())

        cursor = self.db_connection.cursor()

        if position == 'above':
            # 插入上方：新步驟編號 = 目前編號 - 5
            new_step_no = current_step_no - 5
        else:
            # 插入下方：新步驟編號 = 目前編號 + 5
            new_step_no = current_step_no + 5

        # 檢查編號是否已存在
        cursor.execute('SELECT COUNT(*) FROM steps where project_id = ? and step_no = ?',
                      (self.current_project_id, new_step_no))
        if cursor.fetchone()[0] > 0:
            QMessageBox.warning(self, '警告', f'步驟編號 {new_step_no} 已存在')
            return

        cursor.execute('''
            INSERT INTO steps (project_id, step_no, enabled, action_description)
            VALUES (?, ?, 1, '新步驟')
        ''', (self.current_project_id, new_step_no))

        self.db_connection.commit()
        self.load_steps()

    def batch_enable_disable(self, direction, enable):
        """批次啟用/停用步驟"""
        current_row = self.steps_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, '警告', '請選擇步驟')
            return

        current_step_no = int(self.steps_table.item(current_row, 0).text())
        cursor = self.db_connection.cursor()

        if direction == 'above':
            # 以上全部
            cursor.execute('''
                UPDATE steps SET enabled = ?
                where project_id = ? and step_no <= ?
            ''', (enable, self.current_project_id, current_step_no))
        else:
            # 以下全部
            cursor.execute('''
                UPDATE steps SET enabled = ?
                where project_id = ? and step_no >= ?
            ''', (enable, self.current_project_id, current_step_no))

        self.db_connection.commit()
        self.load_steps()

    def show_context_menu(self, position):
        """顯示右鍵選單"""
        menu = QMenu()

        # 新增步驟選項
        add_above_action = QAction('增加步驟 (上方)', self)
        add_above_action.triggered.connect(lambda: self.add_step_at_position('above'))
        menu.addAction(add_above_action)

        add_below_action = QAction('增加步驟 (下方)', self)
        add_below_action.triggered.connect(lambda: self.add_step_at_position('below'))
        menu.addAction(add_below_action)

        menu.addSeparator()

        delete_action = QAction('刪除步驟', self)
        delete_action.triggered.connect(self.delete_step)
        menu.addAction(delete_action)

        menu.addSeparator()

        # 批次操作
        enable_above_action = QAction('以上全部 enable', self)
        enable_above_action.triggered.connect(lambda: self.batch_enable_disable('above', True))
        menu.addAction(enable_above_action)

        disable_below_action = QAction('以下全部 disable', self)
        disable_below_action.triggered.connect(lambda: self.batch_enable_disable('below', False))
        menu.addAction(disable_below_action)

        menu.exec_(self.steps_table.mapToGlobal(position))

    def closeEvent(self, a0: Optional[QCloseEvent]) -> None:
        try:
            # 儲存 UI 設定
            self.save_ui_settings()

            if self.db_connection:
                self.db_connection.close()
                self.db_connection = None
        except Exception as e:
            print(f"關閉資料庫連接時發生錯誤: {str(e)}")

        if a0:
            a0.accept()
        super().closeEvent(a0)


class CreateProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('建立新專案')
        self.setModal(True)

        layout = QVBoxLayout(self)

        name_layout = QHBoxLayout()
        name_label = QLabel('專案名稱：')
        self.project_name_edit = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.project_name_edit)
        layout.addLayout(name_layout)

        # 按區域
        button_layout = QHBoxLayout()

        # 存檔案按
        save_btn = QPushButton('存入檔案')
        save_btn.clicked.connect(self.save_to_file)
        button_layout.addWidget(save_btn)

        # 關閉按
        close_btn = QPushButton('關閉')
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def save_to_file(self):
        """將程式碼儲存到檔案"""
        try:
            with open('test_step.py', 'w', encoding='utf-8') as f:
                f.write(self.code_edit.toPlainText())
            QMessageBox.information(self, '成功', '程式碼已儲存到 test_step.py')
        except Exception as e:
            QMessageBox.critical(self, '錯誤', f'儲存檔案失敗: {str(e)}')


class CopyProjectDialog(QDialog):
    def __init__(self, current_project_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle('複製專案')
        self.setModal(True)

        layout = QVBoxLayout(self)

        # 目前專案
        current_layout = QHBoxLayout()
        current_label = QLabel('目前專案：')
        self.current_project_label = QLabel(current_project_name)
        current_layout.addWidget(current_label)
        current_layout.addWidget(self.current_project_label)
        current_layout.addStretch()
        layout.addLayout(current_layout)

        # 新專案名稱
        name_layout = QHBoxLayout()
        name_label = QLabel('新專案名稱：')
        self.new_project_name_edit = QLineEdit()
        self.new_project_name_edit.setText(f"{current_project_name}_copy")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.new_project_name_edit)
        layout.addLayout(name_layout)

        # 按區域
        button_layout = QHBoxLayout()

        copy_btn = QPushButton('複製')
        copy_btn.clicked.connect(self.accept)
        button_layout.addWidget(copy_btn)

        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)


class RunStepsDialog(QDialog):
    def __init__(self, steps, parent=None):
        super().__init__(parent)
        self.steps = steps
        self.setWindowTitle('執行步驟')
        self.setModal(True)
        self.resize(800, 600)

        layout = QVBoxLayout(self)

        # 字體控制區域
        font_control_layout = QHBoxLayout()

        self.font_size = 10
        self.is_bold = False

        increase_font_btn = QPushButton('放大字體')
        increase_font_btn.clicked.connect(self.increase_font_size)
        font_control_layout.addWidget(increase_font_btn)

        decrease_font_btn = QPushButton('縮小字體')
        decrease_font_btn.clicked.connect(self.decrease_font_size)
        font_control_layout.addWidget(decrease_font_btn)

        toggle_bold_btn = QPushButton('粗體')
        toggle_bold_btn.setCheckable(True)
        toggle_bold_btn.clicked.connect(self.toggle_bold)
        font_control_layout.addWidget(toggle_bold_btn)

        font_control_layout.addStretch()
        layout.addLayout(font_control_layout)

        # 步驟列表
        self.steps_text = QTextEdit()
        self.steps_text.setReadOnly(True)
        self.steps_text.setFont(QFont('Calibri', self.font_size))
        self.generate_steps_code()
        layout.addWidget(self.steps_text)

        # 按區域
        button_layout = QHBoxLayout()

        run_btn = QPushButton('執行')
        run_btn.clicked.connect(self.run_steps)
        button_layout.addWidget(run_btn)

        save_btn = QPushButton('儲存到檔案')
        save_btn.clicked.connect(self.save_to_file)
        button_layout.addWidget(save_btn)

        close_btn = QPushButton('關閉')
        close_btn.clicked.connect(self.reject)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def increase_font_size(self):
        """增大字體大小"""
        self.font_size += 1
        self.update_font()

    def decrease_font_size(self):
        """減小字體大小"""
        if self.font_size > 8:
            self.font_size -= 1
            self.update_font()

    def toggle_bold(self, checked):
        """切換粗體"""
        self.is_bold = checked
        self.update_font()

    def update_font(self):
        """更新字體設定"""
        font = QFont('Calibri', self.font_size)
        font.setBold(self.is_bold)
        self.steps_text.setFont(font)

    def generate_steps_code(self):
        """生成步驟程式碼"""
        from PyQt5.QtGui import QTextCharFormat, QColor
        from PyQt5.QtWidgets import QTextEdit
        from PyQt5.QtCore import Qt

        code_lines = []
        code_lines.append("import pyautogui")
        code_lines.append("import time")
        code_lines.append("import pyperclip")
        code_lines.append("")
        code_lines.append("# 自動化腳本")
        code_lines.append("def run_automation():")
        code_lines.append("    # 步驟執行")

        # 設定高亮格式
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(0, 128, 0))  # 綠色

        # 生成程式碼並高亮註解
        cursor = self.steps_text.textCursor()
        cursor.beginEditBlock()

        for step in self.steps:
            step_no, enabled, action_desc, keyboard, mouse, x, y, duration, data, interval, delay, repeat = step

            if delay and delay > 0:
                line = f"    time.sleep({delay:.1f})  # 延遲 {delay} 秒"
                cursor.insertText(line + '\n')
                self.highlight_comment(cursor, line, comment_format)

            if mouse and x is not None and y is not None:
                line = f"    # 步驟 {step_no}: {action_desc}"
                cursor.insertText(line + '\n')
                self.highlight_comment(cursor, line, comment_format)

                line = f"    pyautogui.moveTo({x}, {y})"
                cursor.insertText(line + '\n')

                if action_desc.lower() == 'click':
                    cursor.insertText("    pyautogui.click()\n")
                if duration and duration > 0:
                    cursor.insertText(f"    pyautogui.sleep({duration:.1f})\n")
                else:
                    cursor.insertText("    pyautogui.sleep(0.1)\n")

            if keyboard and action_desc:
                line = f"    # 步驟 {step_no}: {action_desc}"
                cursor.insertText(line + '\n')
                self.highlight_comment(cursor, line, comment_format)

                if action_desc.lower().startswith('hotkey'):
                    keys = action_desc.replace('hotkey(', '').replace(')', '').split(',')
                    keys = [k.strip().strip("'\"") for k in keys]
                    cursor.insertText(f"    pyautogui.hotkey({', '.join([repr(k) for k in keys])})\n")
                    if delay and delay > 0:
                        cursor.insertText(f"    time.sleep({delay:.1f})\n")
                    else:
                        cursor.insertText("    time.sleep(0.1)\n")
                elif action_desc.lower().startswith('press'):
                    key = action_desc.replace('press(', '').replace(')', '').strip().strip("'\"")
                    cursor.insertText(f"    pyautogui.press('{key}')\n")
                    if delay and delay > 0:
                        cursor.insertText(f"    time.sleep({delay:.1f})\n")
                    else:
                        cursor.insertText("    time.sleep(0.1)\n")
                elif action_desc.lower() == 'write':
                    cursor.insertText(f"    pyperclip.copy('{data}')  # 將文字複製到剪貼簿\n")
                    cursor.insertText("    time.sleep(0.1)  # 等待剪貼簿穩定（視系統而定）\n")
                    cursor.insertText("    pyautogui.hotkey('ctrl', 'v')  # 模擬 Ctrl+V 貼上\n")
                    if delay and delay > 0:
                        cursor.insertText(f"    pyautogui.sleep({delay:.1f})\n")
                    else:
                        cursor.insertText("    pyautogui.sleep(0.1)\n")

            if interval and interval > 0:
                line = f"    time.sleep({interval:.1f})  # 間隔 {interval} 秒"
                cursor.insertText(line + '\n')
                self.highlight_comment(cursor, line, comment_format)

        cursor.insertText("\n# 行自動化\n")
        cursor.insertText("if __name__ == \"__main__\":\n")
        cursor.insertText("    run_automation()\n")

        cursor.endEditBlock()

    def highlight_comment(self, cursor, line, format):
        """高亮顯示註解部分"""
        comment_pos = line.find('#')
        if comment_pos >= 0:
            # 使用 QTextCursor 的移動操作
            cursor.movePosition(QTextCursor.PreviousBlock)
            cursor.movePosition(QTextCursor.EndOfLine)
            cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, len(line) - comment_pos)
            cursor.mergeCharFormat(format)
            cursor.movePosition(QTextCursor.NextBlock)

    def run_steps(self):
        """執行步驟"""
        try:
            exec(self.steps_text.toPlainText())
            QMessageBox.information(self, '成功', '步驟執行完成')
        except Exception as e:
            QMessageBox.critical(self, '錯誤', f'執行失敗: {str(e)}')

    def save_to_file(self):
        """將程式碼儲存到檔案"""
        try:
            with open('test_step.py', 'w', encoding='utf-8') as f:
                f.write(self.steps_text.toPlainText())
            QMessageBox.information(self, '成功', '程式碼已儲存到 test_step.py')
        except Exception as e:
            QMessageBox.critical(self, '錯誤', f'儲存檔案失敗: {str(e)}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = StepToolsApp()
    window.show()
    sys.exit(app.exec_())