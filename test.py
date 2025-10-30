pyautogui.moveTo(300, 170)  # 移動滑鼠到座標 (100, 200)

pyautogui.click()                # 點擊目前位置

pyautogui.sleep(2)                           # 等待 2 秒

pyautogui.moveTo(180, 170)  # 移動滑鼠到座標 (100, 200)

pyautogui.click()                # 點擊目前位置

pyautogui.sleep(2)                           # 等待 2 秒

pyautogui.moveTo(300, 170)  # 移動滑鼠到座標 (100, 200)

pyautogui.click()                # 點擊目前位置


pyautogui.sleep(2) 

pyautogui.press('f12')

pyautogui.sleep(2) 

pyautogui.press('f12')

pyautogui.sleep(2) 


lang_jp = pyautogui.locateOnScreen("image\\jp.png")
    print(f"日文位置: {lang_jp}")
    pyautogui.sleep(2)                           # 等待 2 秒

    pyautogui.moveTo(1780, 143)  # 移動滑鼠到語系
    pyautogui.sleep(2)

    lang_en = pyautogui.locateOnScreen("image\\英文.png")
    print(f"英文位置: {lang_en}")
    pyautogui.moveTo(1780, 143)  # 移動滑鼠到語系
    pyautogui.sleep(2)

    lang_cn = pyautogui.locateOnScreen("image\\簡體中文.png")
    print(f"簡體中文位置: {lang_cn}")
    pyautogui.moveTo(1780, 143)  # 移動滑鼠到語系
    pyautogui.sleep(2)

    pyautogui.moveTo(1877, 145)  # 移動滑鼠到切換主題
    pyautogui.sleep(2)                           # 等待 2 秒
