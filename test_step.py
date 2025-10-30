import pyautogui
import time
import pyperclip

# 自動化腳本
def run_automation():
    # 步驟執行
    time.sleep(1.0)  # 延遲 1.0 秒
    # 步驟 20: moveTo
    pyautogui.moveTo(183, 62)
    pyautogui.sleep(0.1)
    time.sleep(1.0)  # 延遲 1.0 秒
    # 步驟 30: click
    pyautogui.moveTo(183, 62)
    pyautogui.click()
    pyautogui.sleep(0.1)
    time.sleep(1.0)  # 延遲 1.0 秒
    # 步驟 40: moveTo
    pyautogui.moveTo(292, 111)
    pyautogui.sleep(0.1)
    time.sleep(1.0)  # 延遲 1.0 秒
    # 步驟 50: click
    pyautogui.moveTo(292, 111)
    pyautogui.click()
    pyautogui.sleep(0.1)
    time.sleep(1.0)  # 延遲 1.0 秒
    # 步驟 60: hotkey('ctrl', 'a')
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(1.0)
    time.sleep(0.5)  # 延遲 0.5 秒
    # 步驟 70: press('delete')
    pyautogui.press('delete')
    time.sleep(0.5)
    time.sleep(1.0)  # 延遲 1.0 秒
    # 步驟 80: write
    pyperclip.copy('5300')  # 將文字複製到剪貼簿
    time.sleep(0.1)  # 等待剪貼簿穩定（視系統而定）
    pyautogui.hotkey('ctrl', 'v')  # 模擬 Ctrl+V 貼上
    pyautogui.sleep(1.0)
    time.sleep(1.0)  # 延遲 1.0 秒
    # 步驟 90: moveTo
    pyautogui.moveTo(89, 163)
    pyautogui.sleep(0.1)
    time.sleep(1.0)  # 延遲 1.0 秒
    # 步驟 100: click
    pyautogui.moveTo(89, 163)
    pyautogui.click()
    pyautogui.sleep(0.1)
    time.sleep(1.0)  # 延遲 1.0 秒
    # 步驟 110: hotkey('ctrl', 'a')
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(1.0)
    time.sleep(1.0)  # 延遲 1.0 秒
    # 步驟 120: press('delete')
    pyautogui.press('delete')
    time.sleep(1.0)
    time.sleep(1.0)  # 延遲 1.0 秒
    # 步驟 130: write
    pyperclip.copy('Hello world')  # 將文字複製到剪貼簿
    time.sleep(0.1)  # 等待剪貼簿穩定（視系統而定）
    pyautogui.hotkey('ctrl', 'v')  # 模擬 Ctrl+V 貼上
    pyautogui.sleep(1.0)
    time.sleep(1.0)  # 延遲 1.0 秒
    # 步驟 140: moveTo
    pyautogui.moveTo(89, 191)
    pyautogui.sleep(0.1)
    time.sleep(1.0)  # 延遲 1.0 秒
    # 步驟 150: click
    pyautogui.moveTo(89, 191)
    pyautogui.click()
    pyautogui.sleep(0.1)
    time.sleep(1.0)  # 延遲 1.0 秒
    # 步驟 160: hotkey('ctrl', 'a')
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(1.0)
    time.sleep(1.0)  # 延遲 1.0 秒
    # 步驟 170: press('delete')
    pyautogui.press('delete')
    time.sleep(1.0)

# 執行自動化
if __name__ == "__main__":
    run_automation()