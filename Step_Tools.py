import sys
import sqlite3
import os
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QTableWidget, QTableWidgetItem,
                             QPushButton, QLineEdit, QLabel, QComboBox,
                             QInputDialog, QTextEdit, QDialog, QMessageBox,
                             QCheckBox, QHeaderView, QAbstractItemView,
                             QMenu, QAction, QShortcut)
from PyQt5.QtGui import (QTextCursor, QKeySequence, QTextCharFormat,
                        QColor, QFont, QIcon, QKeyEvent, QCloseEvent)
from PyQt5.QtCore import Qt, QTimer, QEvent
from PyQt5.QtWidgets import QHeaderView, QTableWidgetItem
from typing import Optional, cast
import pyautogui
import time
import pyperclip

class StepToolsApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_connection = None
        self.current_project_id = None
        self.init_database()
        self.init_ui()
        self.load_projects()

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
            return True
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"無法連接資料庫: {str(e)}")
            self.db_connection = None
            return False

        # 建立專案表格
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

    def init_ui(self):
        """初始化使用者介面"""
        self.setWindowTitle('步驟工具管理系統')
        self.setGeometry(100, 100, 1200, 800)

        # 建立中央 widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主佈局
        main_layout = QVBoxLayout(central_widget)

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

        # 步驟表格
        self.steps_table = QTableWidget()
        self.setup_steps_table()
        main_layout.addWidget(self.steps_table)

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
    def setup_projects_list(self):
        """設定專案列表表格"""
        headers = ['專案名稱', '建立日期', '建立者']
        self.projects_list.setColumnCount(len(headers))
        self.projects_list.setHorizontalHeaderLabels(headers)

        # 設定欄位寬度
        self.projects_list.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.projects_list.setAlternatingRowColors(True)
        self.projects_list.setSelectionBehavior(QAbstractItemView.SelectRows)
    def load_projects_list(self):
        """載入專案列表到表格"""
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT project_name, create_date, create_user FROM projects ORDER BY create_date DESC')

        projects = cursor.fetchall()
        self.projects_list.setRowCount(len(projects))

        for row, project in enumerate(projects):
            # 專案名稱
            name_item = QTableWidgetItem(project[0])
            self.projects_list.setItem(row, 0, name_item)

            # 建立日期
            date_item = QTableWidgetItem(project[1])
            self.projects_list.setItem(row, 1, date_item)

            # 建立者
            user_item = QTableWidgetItem(project[2])
            self.projects_list.setItem(row, 2, user_item)
    def copy_project(self):
        """複製專案"""
        current_row = self.projects_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, '警告', '請選擇要複製的專案')
            return

        source_project_name = self.projects_list.item(current_row, 0).text()

        # 輸入新專案名稱
        new_name, ok = QInputDialog.getText(self, '複製專案', '輸入新專案名稱：', text=f"{source_project_name}_copy")
        if not ok or not new_name.strip():
            return

        new_project_name = new_name.strip()

        # 檢查名稱是否已存在
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM projects WHERE project_name = ?', (new_project_name,))
        if cursor.fetchone()[0] > 0:
            QMessageBox.warning(self, '警告', f'專案名稱 "{new_project_name}" 已存在')
            return

        # 複製專案
        import uuid
        new_project_id = str(uuid.uuid4())

        # 複製專案資訊
        cursor.execute('''
            INSERT INTO projects (project_id, project_name, create_date, create_user)
            SELECT ?, ?, datetime('now'), create_user
            FROM projects WHERE project_name = ?
        ''', (new_project_id, new_project_name, source_project_name))

        # 複製所有步驟
        cursor.execute('''
            INSERT INTO steps (project_id, step_no, enabled, action_description,
                               keyboard_action, mouse_action, coord_x, coord_y,
                               duration, data, interval, delay_time, repeat_count)
            SELECT ?, step_no, enabled, action_description,
                   keyboard_action, mouse_action, coord_x, coord_y,
                   duration, data, interval, delay_time, repeat_count
            FROM steps WHERE project_id = (SELECT project_id FROM projects WHERE project_name = ?)
        ''', (new_project_id, source_project_name))

        self.db_connection.commit()

        # 重新載入專案列表
        self.load_projects()
        self.load_projects_list()

        QMessageBox.information(self, '成功', f'專案 "{source_project_name}" 已複製為 "{new_project_name}"')

    def copy_project_from_name(self, source_project_name, new_project_name):
        """從專案名稱複製專案"""
        # 檢查名稱是否已存在
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM projects WHERE project_name = ?', (new_project_name,))
        if cursor.fetchone()[0] > 0:
            QMessageBox.warning(self, '警告', f'專案名稱 "{new_project_name}" 已存在')
            return

        # 複製專案
        import uuid
        new_project_id = str(uuid.uuid4())

        # 複製專案資訊
        cursor.execute('''
            INSERT INTO projects (project_id, project_name, create_date, create_user)
            SELECT ?, ?, datetime('now'), create_user
            FROM projects WHERE project_name = ?
        ''', (new_project_id, new_project_name, source_project_name))

        # 複製所有步驟
        cursor.execute('''
            INSERT INTO steps (project_id, step_no, enabled, action_description,
                               keyboard_action, mouse_action, coord_x, coord_y,
                               duration, data, interval, delay_time, repeat_count)
            SELECT ?, step_no, enabled, action_description,
                   keyboard_action, mouse_action, coord_x, coord_y,
                   duration, data, interval, delay_time, repeat_count
            FROM steps WHERE project_id = (SELECT project_id FROM projects WHERE project_name = ?)
        ''', (new_project_id, source_project_name))

        self.db_connection.commit()

        # 重新載入專案列表
        self.load_projects()

        QMessageBox.information(self, '成功', f'專案 "{source_project_name}" 已複製為 "{new_project_name}"')

    def rename_project(self):
        """重新命名專案"""
        current_row = self.projects_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, '警告', '請選擇要重新命名的專案')
            return

        old_project_name = self.projects_list.item(current_row, 0).text()

        # 輸入新專案名稱
        new_name, ok = QInputDialog.getText(self, '重新命名專案', '輸入新專案名稱：', text=old_project_name)
        if not ok or not new_name.strip():
            return

        new_project_name = new_name.strip()

        # 檢查名稱是否已存在
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM projects WHERE project_name = ? AND project_name != ?', (new_project_name, old_project_name))
        if cursor.fetchone()[0] > 0:
            QMessageBox.warning(self, '警告', f'專案名稱 "{new_project_name}" 已存在')
            return

        # 更新專案名稱
        cursor.execute('UPDATE projects SET project_name = ? WHERE project_name = ?', (new_project_name, old_project_name))
        self.db_connection.commit()

        # 重新載入專案列表
        self.load_projects()
        self.load_projects_list()

        QMessageBox.information(self, '成功', f'專案 "{old_project_name}" 已重新命名為 "{new_project_name}"')


    def delete_project(self):
        """刪除專案"""
        current_row = self.projects_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, '警告', '請選擇要刪除的專案')
            return

        project_name = self.projects_list.item(current_row, 0).text()

        # 確認刪除
        reply = QMessageBox.question(self, '確認刪除',
                                   f'確定要刪除專案 "{project_name}" 嗎？\n這將刪除專案及其所有步驟資料。',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

        cursor = self.db_connection.cursor()

        # 刪除專案及其步驟
        cursor.execute('DELETE FROM steps WHERE project_id = (SELECT project_id FROM projects WHERE project_name = ?)', (project_name,))
        cursor.execute('DELETE FROM projects WHERE project_name = ?', (project_name,))

        self.db_connection.commit()

        # 重新載入專案列表
        self.load_projects()
        self.load_projects_list()

        QMessageBox.information(self, '成功', f'專案 "{project_name}" 已刪除')

        # 設定 F12 鍵觸發選單
        self.shortcut = QShortcut(QKeySequence("F12"), self)
        self.shortcut.activated.connect(self.trigger_context_menu)

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
                WHERE project_id = ? AND step_no = ?
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
            WHERE project_id = ? AND enabled = 1
            ORDER BY step_no
        ''', (self.current_project_id,))

        steps = cursor.fetchall()
        if not steps:
            QMessageBox.warning(self, '警告', '沒有啟用的步驟')
            return

        # 顯示執行確認對話框
        dialog = RunStepsDialog(steps, self)
        dialog.exec_()

    def trigger_context_menu(self):
        """觸發功能選單"""
        current_row = self.steps_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, '警告', '請選擇一個步驟')
            return

        position = self.steps_table.visualItemRect(self.steps_table.item(current_row, 0)).topLeft()
        self.show_context_menu(self.steps_table.viewport().mapToGlobal(position))

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
        cursor.execute('SELECT COUNT(*) FROM steps WHERE project_id = ? AND step_no = ?',
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
                WHERE project_id = ? AND step_no <= ?
            ''', (enable, self.current_project_id, current_step_no))
        else:
            # 以下全部
            cursor.execute('''
                UPDATE steps SET enabled = ?
                WHERE project_id = ? AND step_no >= ?
            ''', (enable, self.current_project_id, current_step_no))

        self.db_connection.commit()
        self.load_steps()

    def keyPressEvent(self, a0: Optional[QKeyEvent]) -> None:
        """處理鍵盤事件"""
        if not a0 or not self.steps_table:
            return super().keyPressEvent(a0)
        
        try:
            if a0.key() == Qt.Key.Key_F12:
                # 獲取表格中心位置作為選單位置
                center = self.steps_table.rect().center()
                global_pos = self.steps_table.mapToGlobal(center)
                self.show_context_menu(self.steps_table.mapFromGlobal(global_pos))
            else:
                super().keyPressEvent(a0)
        except Exception as e:
            print(f"鍵盤事件處理錯誤: {str(e)}")
            super().keyPressEvent(a0)
        if a0.key() == Qt.Key.Key_F12:
            # 獲取表格中心位置作為選單位置
            center = self.steps_table.rect().center()
            global_pos = self.steps_table.mapToGlobal(center)
            self.show_context_menu(self.steps_table.mapFromGlobal(global_pos))
        else:
            super().keyPressEvent(a0)

    def closeEvent(self, a0: Optional[QCloseEvent]) -> None:
        """關閉事件"""
        try:
            if self.db_connection:
                self.db_connection.close()
                self.db_connection = None
        except Exception as e:
            print(f"關閉資料庫連接時發生錯誤: {str(e)}")
        
        if a0:
            a0.accept()
        super().closeEvent(a0)
        if self.db_connection:
            self.db_connection.close()
        a0.accept()


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

        # 按鈕區域
        button_layout = QHBoxLayout()

        # 儲存檔案按鈕
        save_btn = QPushButton('存入檔案')
        save_btn.clicked.connect(self.save_to_file)
        button_layout.addWidget(save_btn)

        # 關閉按鈕
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

        # 按鈕區域
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

        # 按鈕區域
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

        cursor.insertText("\n# 執行自動化\n")
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