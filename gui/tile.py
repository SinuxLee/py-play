import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox
import tkinter.font as tkfont
import os

try:
    from PIL import ImageGrab
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False


class Whiteboard(tk.Canvas):
    def __init__(self, master, status_callback=None, **kwargs):
        super().__init__(master, bg="white", highlightthickness=0, **kwargs)
        self.tool = tk.StringVar(value="pen")
        self.color = "#2E7D32"
        self.size = tk.IntVar(value=4)
        self._last = None
        self._current_stroke = []
        self._strokes = []
        self._status_callback = status_callback

        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<B1-Motion>", self._on_move)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Motion>", self._on_motion_only)

    def set_color(self, color):
        if color:
            self.color = color
            self._report_status()

    def set_tool(self, tool):
        self.tool.set(tool)
        self._report_status()

    def set_size(self, size):
        try:
            self.size.set(int(size))
        except Exception:
            pass
        self._report_status()

    def clear(self):
        self.delete("all")
        self._strokes.clear()
        self._current_stroke.clear()
        self._last = None
        self._report_status("画布已清空")

    def undo(self):
        if not self._strokes:
            self._report_status("无可撤销操作")
            return
        stroke = self._strokes.pop()
        for item in stroke:
            self.delete(item)
        self._report_status("撤销一次")

    def save_image(self):
        filetypes = [("PNG Image", "*.png")]
        if not PIL_AVAILABLE:
            filetypes.append(("PostScript", "*.ps"))
        path = filedialog.asksaveasfilename(
            title="保存白板",
            defaultextension=".png",
            filetypes=filetypes
        )
        if not path:
            return

        if PIL_AVAILABLE and path.lower().endswith(".png"):
            try:
                self.update()
                x = self.winfo_rootx()
                y = self.winfo_rooty()
                w = self.winfo_width()
                h = self.winfo_height()
                bbox = (x, y, x + w, y + h)
                img = ImageGrab.grab(bbox=bbox)
                img.save(path, "PNG")
                self._report_status(f"已保存: {os.path.basename(path)}")
                return
            except Exception as e:
                messagebox.showwarning("保存失败", f"PNG 保存失败，将尝试 PostScript。\n错误: {e}")

        try:
            ps = self.postscript(colormode="color")
            if not path.lower().endswith(".ps"):
                path = path + ".ps"
            with open(path, "w", encoding="utf-8", errors="ignore") as f:
                f.write(ps)
            self._report_status("已保存为 PostScript")
        except Exception as e:
            messagebox.showerror("保存失败", str(e))

    def _on_press(self, event):
        self._last = (event.x, event.y)
        self._current_stroke = []

    def _on_move(self, event):
        if self._last is None:
            return
        x0, y0 = self._last
        x1, y1 = event.x, event.y
        fill = self.color if self.tool.get() == "pen" else self["bg"]
        item = self.create_line(x0, y0, x1, y1,
                                capstyle=tk.ROUND,
                                smooth=True,
                                width=self.size.get(),
                                fill=fill)
        self._current_stroke.append(item)
        self._last = (x1, y1)
        self._report_status()

    def _on_release(self, event):
        if self._current_stroke:
            self._strokes.append(self._current_stroke[:])
        self._current_stroke.clear()
        self._last = None

    def _on_motion_only(self, event):
        self._report_status(mouse=(event.x, event.y))

    def _report_status(self, msg=None, mouse=None):
        if not self._status_callback:
            return
        info = {
            "tool": self.tool.get(),
            "color": self.color,
            "size": self.size.get(),
            "mouse": mouse
        }
        self._status_callback(info, msg)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("工程模板 - 桌面应用 (Tkinter)")
        self._configure_scaling()
        self._create_style()
        self._build_menu()
        self._build_toolbar()
        self._build_main_area()
        self._build_statusbar()
        self._set_initial_size_and_center()
        # 在窗口显示后设置初始分割条位置
        self.after(150, self._init_panes_positions)

    def _configure_scaling(self):
        try:
            self.tk.call("tk", "scaling", 1.25)
        except Exception:
            pass

    def _create_style(self):
        style = ttk.Style(self)
        for t in ["vista", "clam", "default"]:
            try:
                style.theme_use(t)
                break
            except Exception:
                continue
        
        # 设置默认字体（参考 VS Code、Figma 等成熟工具的字体大小）
        default_font = tkfont.nametofont("TkDefaultFont")
        try:
            default_font.configure(family="Microsoft YaHei UI", size=11)
        except:
            try:
                default_font.configure(family="苹方-简", size=11)
            except:
                default_font.configure(size=11)
        
        text_font = tkfont.nametofont("TkTextFont")
        text_font.configure(size=11)
        
        menu_font = tkfont.nametofont("TkMenuFont")
        try:
            menu_font.configure(size=10)
        except:
            pass
        
        # 按钮、标签等组件的字体配置
        style.configure("TFrame", padding=5)
        style.configure("TLabelframe", padding=10, font=("", 11))
        style.configure("TLabelframe.Label", font=("", 11))
        style.configure("TButton", font=("", 10), padding=(8, 5))
        style.configure("TRadiobutton", font=("", 10))
        style.configure("TLabel", font=("", 10))
        style.configure("Status.TLabel", anchor="w", padding=(10, 5), font=("", 10))
        style.configure("Toolbar.TButton", padding=(12, 7), font=("", 10))
        style.configure("Title.TLabel", font=("", 12, "bold"))
        
        # 设置 Treeview 字体
        style.configure("Treeview", font=("Microsoft YaHei UI", 10), rowheight=24)
        style.configure("Treeview.Heading", font=("Microsoft YaHei UI", 10, "bold"))

    def _build_menu(self):
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="新建白板", command=self._new_board)
        file_menu.add_command(label="打开...", command=self._open_placeholder)
        file_menu.add_separator()
        file_menu.add_command(label="保存白板...", command=self._save_board)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.quit)
        menubar.add_cascade(label="文件", menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="撤销", command=self._undo)
        edit_menu.add_command(label="清空", command=self._clear)
        menubar.add_cascade(label="编辑", menu=edit_menu)

        view_menu = tk.Menu(menubar, tearoff=0)
        self.show_left = tk.BooleanVar(value=True)
        self.show_right = tk.BooleanVar(value=True)
        view_menu.add_checkbutton(label="显示左侧栏", variable=self.show_left, command=self._toggle_left)
        view_menu.add_checkbutton(label="显示右侧栏", variable=self.show_right, command=self._toggle_right)
        menubar.add_cascade(label="视图", menu=view_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="关于", command=lambda: messagebox.showinfo(
            "关于", "工程模板示例\nTkinter + Ttk\n包含菜单/工具栏/三分栏/状态栏/白板"))
        menubar.add_cascade(label="帮助", menu=help_menu)

        self.config(menu=menubar)

    def _build_toolbar(self):
        bar = ttk.Frame(self, relief="flat", padding=(2, 4, 2, 4))
        
        # 创建带图标的按钮（使用 Unicode 字符作为图标）
        self.btn_new = ttk.Button(bar, text="📄 新建", style="Toolbar.TButton", command=self._new_board)
        self.btn_save = ttk.Button(bar, text="💾 保存", style="Toolbar.TButton", command=self._save_board)
        self.btn_undo = ttk.Button(bar, text="↶ 撤销", style="Toolbar.TButton", command=self._undo)
        self.btn_clear = ttk.Button(bar, text="🗑 清空", style="Toolbar.TButton", command=self._clear)

        self.btn_new.pack(side="left", padx=3, pady=2)
        self.btn_save.pack(side="left", padx=3, pady=2)
        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=10, pady=4)
        self.btn_undo.pack(side="left", padx=3, pady=2)
        self.btn_clear.pack(side="left", padx=3, pady=2)

        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=10, pady=4)
        self.btn_pen = ttk.Button(bar, text="✏️ 画笔", style="Toolbar.TButton", command=lambda: self.whiteboard.set_tool("pen"))
        self.btn_eraser = ttk.Button(bar, text="🧹 橡皮", style="Toolbar.TButton", command=lambda: self.whiteboard.set_tool("eraser"))
        self.btn_color = ttk.Button(bar, text="🎨 颜色", style="Toolbar.TButton", command=self._choose_color)

        self.btn_pen.pack(side="left", padx=3, pady=2)
        self.btn_eraser.pack(side="left", padx=3, pady=2)
        self.btn_color.pack(side="left", padx=3, pady=2)

        bar.pack(side="top", fill="x")

    def _build_main_area(self):
        # 水平三分栏
        self.panes = ttk.Panedwindow(self, orient="horizontal")
        self.panes.pack(fill="both", expand=True)

        # 左侧栏
        self.left_frame = ttk.Frame(self.panes)
        self._build_left_sidebar(self.left_frame)
        self.panes.add(self.left_frame, weight=1)

        # 中间
        self.center_frame = ttk.Frame(self.panes)
        self._build_center(self.center_frame)
        self.panes.add(self.center_frame, weight=4)

        # 右侧栏
        self.right_frame = ttk.Frame(self.panes)
        self._build_right_sidebar(self.right_frame)
        self.panes.add(self.right_frame, weight=1)

    def _build_left_sidebar(self, parent):
        title = ttk.Label(parent, text="📁 资源目录", style="Title.TLabel")
        title.pack(anchor="w", padx=6, pady=(4, 10))

        tree_container = ttk.Frame(parent)
        tree_container.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(tree_container, columns=("name",), show="tree", selectmode="browse")
        
        yscroll = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscroll.set)

        self.tree.pack(side="left", fill="both", expand=True)
        yscroll.pack(side="right", fill="y")

        home = os.path.expanduser("~")
        try:
            entries = sorted(os.listdir(home))[:50]
        except Exception:
            entries = []
        root_id = self.tree.insert("", "end", text=home, open=True)
        for name in entries:
            self.tree.insert(root_id, "end", text=name)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

    def _build_center(self, parent):
        info = ttk.Label(parent, text="✨ 白板区域：按住左键绘制（画笔/橡皮），右侧可设置颜色和笔宽",
                         foreground="#555", font=("", 10))
        info.pack(anchor="w", padx=8, pady=(6, 8))

        self.whiteboard = Whiteboard(parent, status_callback=self._update_status_from_whiteboard)
        self.whiteboard.pack(fill="both", expand=True)

    def _build_right_sidebar(self, parent):
        title = ttk.Label(parent, text="⚙️ 属性编辑器", style="Title.TLabel")
        title.pack(anchor="w", padx=6, pady=(4, 10))

        lf_tool = ttk.LabelFrame(parent, text="🛠 工具")
        lf_tool.pack(fill="x", padx=4, pady=6)
        ttk.Radiobutton(lf_tool, text="✏️ 画笔", value="pen", variable=self.whiteboard.tool,
                        command=lambda: self.whiteboard.set_tool("pen")).pack(side="left", padx=8, pady=8)
        ttk.Radiobutton(lf_tool, text="🧹 橡皮", value="eraser", variable=self.whiteboard.tool,
                        command=lambda: self.whiteboard.set_tool("eraser")).pack(side="left", padx=8, pady=8)

        lf_style = ttk.LabelFrame(parent, text="🎨 样式")
        lf_style.pack(fill="x", padx=4, pady=6)
        row = ttk.Frame(lf_style); row.pack(fill="x", padx=8, pady=8)
        ttk.Label(row, text="颜色:").pack(side="left")
        ttk.Button(row, text="选择...", command=self._choose_color).pack(side="left", padx=10)

        row2 = ttk.Frame(lf_style); row2.pack(fill="x", padx=8, pady=8)
        ttk.Label(row2, text="笔宽:").pack(side="left")
        size_scale = ttk.Scale(row2, from_=1, to=40, orient="horizontal")
        size_scale.set(self.whiteboard.size.get())
        size_scale.configure(command=lambda v: self.whiteboard.set_size(float(v)))
        size_scale.pack(side="left", fill="x", expand=True, padx=10)

        lf_ops = ttk.LabelFrame(parent, text="📋 操作")
        lf_ops.pack(fill="x", padx=4, pady=6)
        ttk.Button(lf_ops, text="↶ 撤销", command=self._undo).pack(fill="x", padx=8, pady=5)
        ttk.Button(lf_ops, text="🗑 清空", command=self._clear).pack(fill="x", padx=8, pady=5)
        ttk.Button(lf_ops, text="💾 保存白板...", command=self._save_board).pack(fill="x", padx=8, pady=5)

        parent.pack_propagate(False)

    def _build_statusbar(self):
        self.status = ttk.Label(self, style="Status.TLabel")
        self._set_status_text("就绪")
        self.status.pack(side="bottom", fill="x")

    def _update_status_from_whiteboard(self, info, msg=None):
        tool = "画笔" if info["tool"] == "pen" else "橡皮"
        mouse = info.get("mouse")
        pos = f"  坐标: ({mouse[0]}, {mouse[1]})" if mouse else ""
        extras = f"  模式: {tool}  颜色: {info['color']}  笔宽: {info['size']}"
        base = msg if msg else "绘制中..." if mouse else "就绪"
        self._set_status_text(base + extras + pos)

    def _set_status_text(self, text):
        self.status.config(text=text)

    def _new_board(self):
        if messagebox.askyesno("新建白板", "清空当前白板并新建？"):
            self.whiteboard.clear()

    def _open_placeholder(self):
        filedialog.askopenfilename(title="打开文件")
        self._set_status_text("打开功能预留")

    def _save_board(self):
        self.whiteboard.save_image()

    def _undo(self):
        self.whiteboard.undo()

    def _clear(self):
        if messagebox.askokcancel("清空白板", "确认清空？"):
            self.whiteboard.clear()

    def _choose_color(self):
        color = colorchooser.askcolor(color=self.whiteboard.color, title="选择颜色")
        if color and color[1]:
            self.whiteboard.set_color(color[1])

    def _on_tree_select(self, event):
        item = self.tree.selection()
        if not item:
            return
        text = self.tree.item(item[0], "text")
        self._set_status_text(f"选择: {text}")

    def _toggle_left(self):
        """切换左侧栏显示/隐藏"""
        if self.show_left.get():
            # 显示左侧栏
            if self.left_frame not in self.panes.panes():
                self.panes.insert(0, self.left_frame, weight=1)
            self.after(50, self._init_panes_positions)
        else:
            # 隐藏左侧栏
            try:
                self.panes.forget(self.left_frame)
            except Exception:
                pass
            self.after(50, self._init_panes_positions)

    def _toggle_right(self):
        """切换右侧栏显示/隐藏"""
        if self.show_right.get():
            # 显示右侧栏
            if self.right_frame not in self.panes.panes():
                self.panes.add(self.right_frame, weight=1)
            self.after(50, self._init_panes_positions)
        else:
            # 隐藏右侧栏
            try:
                self.panes.forget(self.right_frame)
            except Exception:
                pass
            self.after(50, self._init_panes_positions)

    def _set_initial_size_and_center(self):
        """设置初始窗口大小并在屏幕居中"""
        # 先更新窗口以获取准确的屏幕尺寸
        self.update_idletasks()
        
        # 获取屏幕尺寸
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        
        # 设置窗口大小（屏幕的 75%，最小 960x640）
        w = max(960, int(sw * 0.75))
        h = max(640, int(sh * 0.75))
        
        # 计算居中位置（重要：需要考虑任务栏和标题栏）
        x = (sw - w) // 2
        y = (sh - h) // 2
        
        # 稍微向上偏移，让视觉上更居中（因为有任务栏）
        y = max(20, y - 20)
        
        # 确保窗口不会超出屏幕范围
        x = max(0, min(x, sw - w))
        y = max(0, min(y, sh - h))
        
        # 设置窗口位置和大小
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.minsize(900, 600)
        
        # 强制窗口显示并居中
        self.update_idletasks()

    def _init_panes_positions(self):
        """在 ttk.Panedwindow 中，用 sashpos 设置初始分隔条位置"""
        self.update_idletasks()
        try:
            total = self.panes.winfo_width()
            if total <= 0:
                # 如果还没布局好，稍后再试一次
                self.after(100, self._init_panes_positions)
                return

            left_w_desired = 240
            right_w_desired = 260

            # 保障总宽度不足时的回退策略
            min_center = 400
            left_w = left_w_desired
            right_w = right_w_desired
            if total < left_w + right_w + min_center:
                # 按比例缩小侧边栏，确保中间至少 min_center
                spare = max(0, total - min_center)
                left_w = int(spare * 0.48)
                right_w = spare - left_w
                left_w = max(160, left_w)
                right_w = max(180, right_w)

            # sash 0 是左/中之间，sash 1 是中/右之间
            if len(self.panes.panes()) >= 2:
                self.panes.sashpos(0, left_w)
            if len(self.panes.panes()) >= 3:
                self.panes.sashpos(1, max(left_w + 200, total - right_w))
        except Exception:
            pass


if __name__ == "__main__":
    app = App()
    app.mainloop()