import pyautogui
import pyscreeze
import time


pyautogui.hotkey('ctrl', 'shift')  # 或 pyautogui.hotkey('alt', 'shift')
time.sleep(0.2)


try:   
 
    pyautogui.moveTo(1780, 143)  # 移動滑鼠到語系
    pyautogui.sleep(2)                           # 等待 2 秒
    pyautogui.click()                # 點擊目前位置
    pyautogui.sleep(1)


    goto_position = pyautogui.locateOnScreen("image\\Jp.jpg", confidence=0.9, grayscale=True)
    print(f"Jp位置: {goto_position}")         
    pyautogui.sleep(2)  

    pyautogui.moveTo(goto_position)  # 移動滑鼠到jp語系
    
    pyautogui.sleep(2)
    pyautogui.click()                # 點擊目前位置
    pyautogui.sleep(2)
  
    
    pyautogui.moveTo(437, 137)  # 移動滑鼠到語系
    pyautogui.sleep(2)                           # 等待 2 秒
    pyautogui.click()                # 點擊目前位置
    pyautogui.sleep(3)


    pyautogui.moveTo(1755, 142)  # 移動滑鼠到語系
    pyautogui.sleep(2)                           # 等待 2 秒
    pyautogui.click()                # 點擊目前位置
    pyautogui.sleep(1)

    pyautogui.moveTo(1787, 220)     # 移動滑鼠到語系
    pyautogui.sleep(2)                           # 等待 2 秒
    pyautogui.click()                # 點擊目前位置
    pyautogui.sleep(1)


    pyautogui.moveTo(1461, 429)  # 點選表格顯示
    pyautogui.sleep(2)                           # 等待 2 秒
    pyautogui.click()                # 點擊目前位置
    pyautogui.sleep(1)
    
except pyautogui.ImageNotFoundException as e:
    print(f"圖片未找到: {e}")
except Exception as e:
    print(f"其他錯誤: {e}")