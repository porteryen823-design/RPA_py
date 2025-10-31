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

    # 記錄點的變數
    point1 = None
    point2 = None
    cross_length = 100
    cross_coords = []  # 存儲十字線座標的列表

    # 滑鼠移動事件
    def on_mouse_move(event):
        # 清除之前的粉紅色十字線和座標文字
        canvas.delete("pink_cross")
        canvas.delete("coord_text")

        # 畫新的粉紅色十字線
        x, y = event.x, event.y
        canvas.create_line(x - cross_length//2, y, x + cross_length//2, y, fill="pink", width=2, tags="pink_cross")
        canvas.create_line(x, y - cross_length//2, x, y + cross_length//2, fill="pink", width=2, tags="pink_cross")

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
        canvas.create_text(text_x, text_y, text=f"({x}, {y})", fill="pink", font=("Arial", 10), tags="coord_text")

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
        menu.add_command(label="3. 存檔", command=save_image)
        menu.add_command(label="4. 清除繪製矩形", command=clear_rectangles)
        menu.add_separator()
        menu.add_command(label="5. 存十字線座標", command=lambda: save_cross_coords(event))
        menu.add_command(label="6. 重新擷取螢幕", command=refresh_screenshot)
        if point1 and point2 and OCR_AVAILABLE:
            menu.add_command(label="7. OCR 功能", command=perform_ocr)
        elif not OCR_AVAILABLE:
            menu.add_command(label="7. OCR 功能 (未安裝)", state="disabled")
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

    def save_image():
        # 儲存當前 canvas 內容為圖片
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        save_path = f"image_temp/screenshot_with_marks_{timestamp}.png"
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
                # 顯示結果視窗
                result_window = tk.Toplevel(root)
                result_window.title("OCR 辨識結果")
                result_window.geometry("400x300")

                text_widget = tk.Text(result_window, wrap=tk.WORD, padx=10, pady=10)
                text_widget.insert(tk.END, text)
                text_widget.config(state=tk.DISABLED)
                text_widget.pack(expand=True, fill=tk.BOTH)

                # 複製到剪貼簿按鈕
                def copy_to_clipboard():
                    root.clipboard_clear()
                    root.clipboard_append(text)
                    print("已複製到剪貼簿")

                copy_btn = tk.Button(result_window, text="複製到剪貼簿", command=copy_to_clipboard)
                copy_btn.pack(pady=5)
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