import pyautogui
import keyboard

def show_position():
    x, y = pyautogui.position()
    print(f"Mouse position: ({x}, {y})")

# 設定熱鍵：Shift + Ctrl + F12 顯示滑鼠座標
keyboard.add_hotkey('shift+ctrl+f12', show_position)

# 按下 Esc 離開程式
keyboard.wait('esc')