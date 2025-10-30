import pyautogui
import pyscreeze
import time
import ctypes

def is_input_language_english():
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    hkl = user32.GetKeyboardLayout(0)
    lang_id = hkl & 0xFFFF
    return lang_id == 0x0409  # 0x0409 是美式英文

def is_input_language_TChinese():
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    hkl = user32.GetKeyboardLayout(0)
    lang_id = hkl & 0xFFFF
    return lang_id == 0x0404  # 0x0404 中文（繁體）

if is_input_language_TChinese():
    print("目前是中文輸入法")
    pyautogui.hotkey('ctrl', 'shift')
else:
    print("目前不是中文輸入法")

    
try:

    # Step 1: 切換回英文輸入法（根據你的系統設定）
    #pyautogui.hotkey('ctrl', 'shift')  # 或 pyautogui.hotkey('alt', 'shift')
    #time.sleep(0.2)    


    pyautogui.moveTo(287, 110)  
    pyautogui.sleep(2)                           # 等待 2 秒
    pyautogui.click()                # 點擊目前位置   
    pyautogui.sleep(1) 

    # Step 3: 全選文字（Ctrl+A）
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.1)

    # Step 4: 清除文字（Delete 或 Backspace）
    pyautogui.press('delete')  # 或 pyautogui.press('backspace')
    time.sleep(0.1)

    # Step 5: 輸入新文字

    pyautogui.write('5300', interval=0.05)
    pyautogui.sleep(2) 

    # Step 4: 模擬 Tab 或 Enter（選擇其一）
    pyautogui.press('tab')    # 跳到下一個欄位
    # pyautogui.press('enter')  # 提交或確認選項
    pyautogui.sleep(0.2) 

   

    pyautogui.press('tab', interval=0.5)    # 跳到下一個欄位
    pyautogui.sleep(0.5)
    pyautogui.press('tab', interval=0.5) 
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.1)
    # Step 4: 清除文字（Delete 或 Backspace）           
    pyautogui.press('delete')  # 或 pyautogui.press('backspace')
    time.sleep(0.1)
    pyautogui.write('ABCD1234', interval=0.1)
    
    pyautogui.press('tab')    # 跳到下一個欄位
    time.sleep(0.1)

    pyautogui.press('tab')    # 跳到下一個欄位
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.1)

    # Step 4: 清除文字（Delete 或 Backspace）
    pyautogui.press('delete')  # 或 pyautogui.press('backspace')
    time.sleep(0.1)
    pyautogui.write('Hello World', interval=0.1)

    pyautogui.press('tab')    # 跳到下一個欄位
    time.sleep(0.1)

    pyautogui.press('tab')
    pyautogui.hotkey('ctrl', 'a')       
    time.sleep(0.1)

    # Step 4: 清除文字（Delete 或 Backspace）
    pyautogui.press('delete')  # 或 pyautogui.press('backspace')
    time.sleep(0.1)    
    pyautogui.write('Hello World 2', interval=0.1)

    pyautogui.moveTo(387, 110)  # 點擊 TCP Connect
    pyautogui.sleep(2)   
    pyautogui.click() 

    pyautogui.moveTo(764, 158)  
    pyautogui.sleep(2)                           # 等待 2 秒
    pyautogui.click()                # 點擊目前位置

    pyautogui.sleep(2)                           # 等待 2 秒
    pyautogui.click()                # 點擊目前位置

    
    pyautogui.moveTo(764, 187)  
    pyautogui.sleep(2)                           # 等待 2 秒
    pyautogui.click()                # 點擊目前位置

    pyautogui.sleep(2)                           # 等待 2 秒
    pyautogui.click()                # 點擊目前位置

    pyautogui.moveTo(387, 110)  # 點擊 TCP Connect
    pyautogui.sleep(2)   
    pyautogui.click() 
   

    pyautogui.moveTo(287, 110)  
    pyautogui.sleep(2)                           # 等待 2 秒
    pyautogui.click()                # 點擊目前位置   
    pyautogui.sleep(1) 

    # Step 3: 全選文字（Ctrl+A）
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.1)

    # Step 4: 清除文字（Delete 或 Backspace）
    pyautogui.press('delete')  # 或 pyautogui.press('backspace')
    time.sleep(0.1)

    # Step 5: 輸入新文字

    pyautogui.write('5200', interval=0.05)
    pyautogui.sleep(2) 
    
except pyautogui.ImageNotFoundException as e:
    print(f"圖片未找到: {e}")
except Exception as e:
    print(f"其他錯誤: {e}")