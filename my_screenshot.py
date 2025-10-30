import pyautogui
import os
import datetime
import time
import threading
from PIL import Image, ImageTk, ImageDraw
import tkinter as tk

def take_screenshot(center_x, center_y, width, height, filename):
    # 計算左上角座標
    left = center_x - width // 2
    top = center_y - height // 2

    # 確保座標不為負
    if left < 0:
        left = 0
    if top < 0:
        top = 0

    # 截取整個螢幕作為底圖
    full_screenshot = pyautogui.screenshot()

    # 截取區域
    screenshot = pyautogui.screenshot(region=(left, top, width, height))

    # 確保 image 目錄存在
    os.makedirs('image_temp', exist_ok=True)

    # 儲存 BMP 和 JPG
    png_path = os.path.join('image_temp', f"{filename}.png")
    bmp_path = os.path.join('image_temp', f"{filename}.bmp")
    jpg_path = os.path.join('image_temp', f"{filename}.jpg")

    screenshot.save(png_path, 'PNG')
    screenshot.save(bmp_path, 'BMP')
    screenshot.save(jpg_path, 'JPEG')

    print(f"截圖已儲存: {png_path}, {bmp_path} 和 {jpg_path}")

    # 在整個螢幕底圖上畫紅色外框標註擷取區域和十字線
    draw = ImageDraw.Draw(full_screenshot)
    draw.rectangle([left, top, left + width, top + height], outline="red", width=3)

    # 在擷取區域中心點畫紅色十字線（長度 100 pixel）
    cross_length = 100
    center_x_img = center_x
    center_y_img = center_y
    draw.line([center_x_img - cross_length//2, center_y_img, center_x_img + cross_length//2, center_y_img], fill="red", width=2)
    draw.line([center_x_img, center_y_img - cross_length//2, center_x_img, center_y_img + cross_length//2], fill="red", width=2)

    # 顯示視窗預覽整個螢幕底圖
    root = tk.Tk()
    root.title("截圖預覽 - 整個螢幕底圖")

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

    # 滑鼠移動事件
    def on_mouse_move(event):
        # 清除之前的粉紅色十字線
        canvas.delete("pink_cross")

        # 畫新的粉紅色十字線
        x, y = event.x, event.y
        canvas.create_line(x - cross_length//2, y, x + cross_length//2, y, fill="pink", width=2, tags="pink_cross")
        canvas.create_line(x, y - cross_length//2, x, y + cross_length//2, fill="pink", width=2, tags="pink_cross")

        # 更新座標顯示
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

    canvas.bind("<Button-3>", show_context_menu)  # 右鍵綁定

    # 設定視窗大小為圖片大小
    root.geometry(f"{full_screenshot.width}x{full_screenshot.height}")
    root.resizable(False, False)
    root.attributes("-topmost", True)  # 確保視窗在最上層

    # 顯示視窗（非阻塞，等待用戶關閉）
    root.mainloop()

if __name__ == "__main__":
    # 直接設定參數
    center_x = 1774  # 中心點 X 座標
    center_y = 280  # 中心點 Y 座標
    width = 150     # 寬度
    height = 50    # 高度
    filename = f"image{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"  # 檔案名稱

    take_screenshot(center_x, center_y, width, height, filename)