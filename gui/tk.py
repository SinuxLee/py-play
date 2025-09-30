import tkinter as tk

# -----------------------------
# 创建主窗口
# -----------------------------
root = tk.Tk()
root.title("绘图示例")

# 固定窗口大小
window_width = 600
window_height = 400
root.geometry(f"{window_width}x{window_height}")
root.resizable(False, False)  # 不可调整大小

# 禁用最大化按钮（仅在 Windows 上生效）
root.attributes('-toolwindow', True)

# -----------------------------
# 创建 Canvas
# -----------------------------
canvas = tk.Canvas(root, bg="white", width=window_width, height=window_height)
canvas.pack(fill=tk.BOTH, expand=True)

# -----------------------------
# 绘制45度网格
# -----------------------------
grid_size = 40  # 网格间距

# 绘制从左下到右上方向的线
for i in range(-window_height, window_width, grid_size):
    canvas.create_line(i, window_height, i + window_height, 0, fill="gray")

# 绘制从左上到右下方向的线
for i in range(0, window_width + window_height, grid_size):
    canvas.create_line(i, 0, i - window_height, window_height, fill="gray")

# -----------------------------
# 运行主循环
# -----------------------------
root.mainloop()
