import pyautogui
from pywinauto.application import Application
import time

# 啟動應用程式
app = Application().start("notepad.exe")

# 等待應用程式啟動
time.sleep(2)

# 連接到已開啟的應用程式，使用 win32 後端
app = Application(backend="win32").connect(title_re=".*.*")

# 操作視窗與元件
notepad = app.window(title_re=".*.*")
edit = notepad.Edit
edit.type_keys("Hello, pywinauto!")
