import tkinter as tk

root = tk.Tk()
root.title("playground")

screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()

win_w = int(screen_w * 0.6)
win_h = int(screen_h * 0.7)

root.geometry(f"{win_w}x{win_h}+{(screen_w - win_w) // 2}+{(screen_h - win_h) // 2}")
root.resizable(False, False)
root.attributes("-toolwindow", True)


canvas = tk.Canvas(root, bg="white", width=win_w, height=win_h)
canvas.pack(fill=tk.BOTH, expand=True)

# 直线
line = canvas.create_line(50, 50, 200, 50, fill="blue", width=2)

# 矩形
rect = canvas.create_rectangle(50, 100, 200, 150, fill="yellow", outline="black")

# 椭圆（用矩形框定）
oval = canvas.create_oval(250, 100, 350, 200, fill="pink")

# 多边形
poly = canvas.create_polygon(100, 200, 150, 250, 50, 250, fill="green")

# 文本
text = canvas.create_text(200, 30, text="Hello Canvas", font=("Arial", 16), fill="red")


# 改变层级
canvas.tag_raise(rect)  # 提到最上层
canvas.tag_lower(oval)  # 放到底层

# 也可以指定参照对象
canvas.tag_raise(rect, oval)  # rect 提到 oval 上面

# 获取最顶/底的 item
top_item = canvas.find_above(oval)
bottom_item = canvas.find_below(oval)


# 图片
# img = tk.PhotoImage(file="example.png")
# canvas.create_image(200, 150, image=img)

# 给元素加 tag
canvas.itemconfig(rect, tags=("shape", "highlight"))

# 按 tag 修改
canvas.itemconfig("shape", fill="orange")

# 移动所有 shape
canvas.move("shape", 20, 0)


def on_click(event):
    print("Clicked at", event.x, event.y)

canvas.bind("<Button-1>", on_click)        # 点击画布
canvas.tag_bind(rect, "<Button-1>", on_click)  # 只点矩形触发


def update(cycle):
    root.after(1000, update, cycle + 1)
    
    match cycle:
        case 0:
            print("Top item:", top_item)
            print("Bottom item:", bottom_item)
        case 1:
            # 移动
            canvas.move(rect, 10, 20)    # x+10, y+20

            # 修改属性
            canvas.itemconfig(rect, fill="blue", outline="red")

            # 获取坐标
            coords = canvas.coords(rect)  # [x1, y1, x2, y2]

            # 修改坐标
            canvas.coords(rect, 60, 120, 210, 170)
            canvas.create_line(0, win_h // 2, win_w, win_h // 2, fill="green", width=3)
        case 2:
            # 画布滚动/偏移
            canvas.xview_moveto(0.5)   # 水平移动到中点
            canvas.yview_scroll(1, "units")

            # 获取画布区域
            bbox = canvas.bbox(rect)   # (x1, y1, x2, y2)
        case 3:
            canvas.delete(rect)        # 删除单个
            canvas.delete("all")       # 删除全部
        case _:
            return

if __name__ == "__main__":
    root.after(1, update, 0)
    root.mainloop()
