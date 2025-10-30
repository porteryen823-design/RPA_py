import pyautogui
import pyscreeze
import time
import ctypes


    
try:

    ViewLoc = pyautogui.locateCenterOnScreen("image\\View.png", confidence=0.9, grayscale=True)
    print(f"View位置: {ViewLoc}")
    pyautogui.sleep(1) 
    
    pyautogui.moveTo(ViewLoc)
    pyautogui.sleep(1)                           # 等待 2 秒
    pyautogui.click()                # 點擊目前位置   

    
except pyautogui.ImageNotFoundException as e:
    print(f"圖片未找到: {e}")
except Exception as e:
    print(f"其他錯誤: {e}")