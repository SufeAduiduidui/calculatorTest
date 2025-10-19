import ast
import math
import time
import tkinter as tk
import customtkinter as ctk

from .pet_widget import PetWidget  # 桌宠
from ..core.safe_eval import SafeEvaluator

from .sound_player import play as play_sound
from .dialogs import show_cat_bubble

from .sound_player import toggle_muted, is_muted
from tkinter import simpledialog, messagebox

from PIL import Image, ImageDraw

class CalculatorPage(ctk.CTkFrame):
    def __init__(self, master, evaluator: SafeEvaluator, palette, theme_name):
        super().__init__(master, corner_radius=12)
        self.evaluator = evaluator
        self._palette = palette
        self._theme_name = theme_name
        self.history = []
        self._func_buttons = []
        self._digit_buttons = []
        self._op_buttons = []
        self._pet_bubble = None
        self._pet_hint_shown = False
        self._pet_click_count = 0
        self._pet_last_click_ts = 0.0
        self._calc_last_values = {}
        self._solve_last_params = {}
        self._solve_last_guess = None
        self._solve_last_var = None
        self._sigma_last_args = {"var": "n", "lower": "1", "upper": "10", "expr": "n"}
        self._pow_last_args = {"base": "2", "exp": "3"}
        self._integral_last_args = {"var": "x", "lower": "0", "upper": "1", "expr": "x"}
        self._derivative_last_var = "x"
        self._build()

    def _make_circle_x_image(self, diameter, color_hex):#没招了，gpt的法子：生成一张：圆为实心、X 为透明挖空 的 RGBA 图片
        D = int(diameter)
        pad = max(1, D // 12)# 圆与边缘留一点空隙，避免被裁切
        thickness = max(2, D // 8)# X 的线宽，可按需要调整

        # 做一张 alpha 掩膜：先画实心圆，再用 0 把 X 两条对角线擦掉
        mask = Image.new("L", (D, D), 0)
        m = ImageDraw.Draw(mask)
        m.ellipse((pad, pad, D - pad - 1, D - pad - 1), fill=255)
        m.line((pad, pad, D - pad - 1, D - pad - 1), fill=0, width=thickness)
        m.line((pad, D - pad - 1, D - pad - 1, pad), fill=0, width=thickness)

        # 用圆的颜色填充，并套上掩膜（X 区域 alpha=0 变透明）
        base = Image.new("RGBA", (D, D), color_hex)
        base.putalpha(mask)

        return ctk.CTkImage(light_image=base, dark_image=base, size=(D, D))


    def _build(self):
        frame = self

        self.device = ctk.CTkScrollableFrame(frame, corner_radius=24)
        self.device.pack(fill="both", expand=True, padx=40, pady=20)

        brand = ctk.CTkFrame(self.device, fg_color="transparent")
        brand.pack(side="top", fill="x", padx=20, pady=(18, 6))

        left = ctk.CTkFrame(brand, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True)

        right = ctk.CTkFrame(brand, fg_color="transparent")
        right.pack(side="right")

        right_row = ctk.CTkFrame(right, fg_color="transparent")
        right_row.pack()

        self.lbl_brand = ctk.CTkLabel(left, text="CASIO", font=("SF Pro Display", 18, "bold"))
        self.lbl_sub = ctk.CTkLabel(left, text="CLASSWIZ", font=("SF Pro Text", 12))
        self.lbl_brand.pack()
        self.lbl_sub.pack()

        self._mute_btn = ctk.CTkButton(
            right_row,
            text=("切换成有声" if is_muted() else "切换成无声"),
            width=54,
            command=self._toggle_mute,
        )
        self._mute_btn.pack(side="left", padx=(0, 6))

        self.pet = PetWidget(
            right_row,
            image_path="assets/pet.jpg",
            size=(64, 64),
            on_click=self._handle_pet_single_click,
            on_triple_click=self._open_pet_calc,
        )
        self.pet.pack(side="left", padx=6, pady=0)

        screen = ctk.CTkFrame(self.device, corner_radius=12)
        screen.pack(fill="x", padx=20, pady=(6, 12))
        scr_row = ctk.CTkFrame(screen, fg_color="transparent")
        scr_row.pack(fill="x", padx=10, pady=8)

        self.expr_var = tk.StringVar()
        self.expr_entry = ctk.CTkEntry(scr_row, textvariable=self.expr_var, height=36, font=("Consolas", 16))
        self.expr_entry.pack(side="left", fill="x", expand=True)
        self.expr_entry.bind("<Return>", lambda e: self.calculate())

        self.mode_lbl = ctk.CTkLabel(scr_row, text=("D" if self.evaluator.deg_mode else "R"), font=("SF Pro Text", 14))
        self.mode_lbl.pack(side="right", padx=(6, 0))

        self.mode_lbl.bind("<Button-1>", lambda e: self._toggle_drg())#DR标签可点击切换角度/弧度
        self.mode_lbl.configure(cursor="hand2")

        self.result_var = tk.StringVar(value="0")
        self.res_lbl = ctk.CTkLabel(screen, textvariable=self.result_var, anchor="e", font=("Consolas", 28))
        self.res_lbl.pack(fill="x", padx=10, pady=(0, 8))



        func_area = ctk.CTkFrame(self.device, corner_radius=14)
        func_area.pack(fill="x", padx=20, pady=(0, 8))

        ind_row = ctk.CTkFrame(func_area, fg_color="transparent")
        ind_row.pack(fill="x", padx=6, pady=(6, 0))

        self._circle_labels = []
        self._circle_middle_lbl = None
        self._circle_middle_img = None
        self._circle_middle_d = None

        circle_sizes = [42, 42, 62, 42, 42]

        for c in range(5):
            ind_row.grid_columnconfigure(c, weight=1, uniform="ind")

        ind_row.grid_rowconfigure(0, weight=1)
        for c, size in enumerate(circle_sizes):
            if c == 2:
                #中间的用图片（圆+X 挖空）
                D = int(size)  # 直径大致按原来的字号来
                color = self._palette.get("subtext", "#6C6C70")
                img = self._make_circle_x_image(D, color)

                lbl = ctk.CTkLabel(ind_row, text="", image=img)
                lbl.grid(row=0, column=c, padx=4, pady=(0, 8), sticky="n")
                lbl.configure(cursor="hand2")
                lbl.bind("<Button-1>", lambda e: self.insert_text("x"))

                self._circle_middle_lbl = lbl
                self._circle_middle_img = img
                self._circle_middle_d = D

                self._circle_labels.append(lbl)
            else:
                ch = "●"
                lbl = ctk.CTkLabel(
                    ind_row,
                    text=ch,
                    font=("SF Pro Text", size),
                    text_color=self._palette.get("subtext", "#6C6C70"),
                )
                lbl.grid(row=0, column=c, padx=4, pady=(0, 8), sticky="n")
                if c == 1:#第2个圆光标左移
                    lbl.configure(cursor="hand2")
                    lbl.bind("<Button-1>", self._move_cursor_left)
                elif c == 3:#第4个圆光标右移
                    lbl.configure(cursor="hand2")
                    lbl.bind("<Button-1>", self._move_cursor_right)
                self._circle_labels.append(lbl)

        funcs = [
            [
                ("SOLVE", self._solve_equation, "func_call", True),
                ("CALC", self._calc_expression, "func_call", True),
                ("x!", self._insert_factorial, "func_call", True),
                ("x^3", self._insert_pow3, "func_call", True),
                ("x^2", self._insert_pow2, "func_call", True),
                #("DRG", self._toggle_drg, "func_call", True),
            ],
            [
                ("sqrt", self._insert_sqrt, "func_call", True),
                ("y√x", self._insert_y_root, "func_call", True),
                ("1/x", self._insert_reciprocal, "func_call", True),
                ("log10", self._insert_log10, "func_call", True),
                ("ln", self._insert_ln, "func_call", True),
            ],
            [
                ("Σ", self._sigma_sum, "func_call", True),
                ("\u03C0", "\u03C0", "func", True),
                ("e", "e", "func", True),
                ("sin", self._insert_sin, "func_call", True),
                ("cos", self._insert_cos, "func_call", True),
            ],
            [
                ("tan", self._insert_tan, "func_call", True),
                ("|x|", self._insert_abs, "func_call", True),
                ("xⁿ", self._power_prompt, "func_call", True),
                ("(", "(", "func", True),
                (")", ")", "func", True),
            ],
            [
                ("∫", self._integral_prompt, "func_call", True),
                ("d/dx", self._derivative_prompt, "func_call", True),
                ("sin^(-1)", self._insert_arcsin, "func_call", True),
                ("cos^(-1)", self._insert_arccos, "func_call", True),
                ("tan^(-1)", self._insert_arctan, "func_call", True),
            ],
        ]

        FUNC_BTN_HEIGHT =30

        for row in funcs:
            rf = ctk.CTkFrame(func_area, fg_color="transparent")
            rf.pack(fill="x", padx=6, pady=4)

            for c in range(len(row)):
                rf.grid_columnconfigure(c, weight=1, uniform="funcs")

            for c, (text, action, kind, enabled) in enumerate(row):
                if kind == "func_call":
                    cmd = action if enabled else None
                else:
                    cmd = (lambda s=action: self.insert_text(s)) if (enabled and isinstance(action, str)) else None

                b = ctk.CTkButton(
                    rf,
                    text=text,
                    height=FUNC_BTN_HEIGHT,
                    corner_radius=10,
                    command=cmd
                )
                b.grid(row=0, column=c, padx=4, sticky="ew")
                self._style_func_button(b, kind="func" if enabled else "ghost", enabled=enabled)
                self._func_buttons.append((b, "func" if enabled else "ghost", enabled))

        keypad = ctk.CTkFrame(self.device, corner_radius=14)
        keypad.pack(fill="x", padx=20, pady=(0, 20))

        row_789 = ["7", "8", "9", "DEL", "AC"]
        row_456 = ["4", "5", "6", "*", "/"]
        row_123 = ["1", "2", "3", "+", "-"]
        row_bottom = ["0", ".", "*10^x", "Ans", "="]

        for row in (row_789, row_456, row_123, row_bottom):
            rf = ctk.CTkFrame(keypad, fg_color="transparent")
            rf.pack(fill="x", padx=6, pady=4, expand=True)
            for label in row:
                if label is None:
                    spacer = ctk.CTkFrame(rf, width=72, height=50, fg_color="transparent")
                    spacer.pack(side="left", padx=4)
                    continue
                if label == "DEL":
                    b = ctk.CTkButton(rf, text=label, height=50, width=80, corner_radius=10, command=self.backspace)
                    b.pack(side="left", padx=4, expand=True, fill="x")
                    self._style_op_button(b, kind="accent")
                    self._op_buttons.append((b, "accent"))
                elif label == "AC":
                    b = ctk.CTkButton(rf, text=label, height=50, width=80, corner_radius=10, command=self.clear_expr)
                    b.pack(side="left", padx=4, expand=True, fill="x")
                    self._style_op_button(b, kind="accent")
                    self._op_buttons.append((b, "accent"))
                elif label == "=":
                    b = ctk.CTkButton(rf, text=label, height=50, width=80, corner_radius=10, command=self.calculate)
                    b.pack(side="left", padx=4, expand=True, fill="x")
                    self._style_op_button(b, kind="equal")
                    self._op_buttons.append((b, "equal"))
                elif label in {"+", "-", "*", "/"}:
                    b = ctk.CTkButton(rf, text=label, height=50, width=80, corner_radius=10,
                                      command=lambda t=label: self.insert_text(t))
                    b.pack(side="left", padx=4, expand=True, fill="x")
                    self._style_op_button(b, kind="op")
                    self._op_buttons.append((b, "op"))
                elif label == "*10^x":
                    b = ctk.CTkButton(
                        rf, text=label, height=50, width=80, corner_radius=10,
                        command=self._insert_ten_power
                    )
                    b.pack(side="left", padx=4, expand=True, fill="x")
                    self._style_digit_button(b, label)
                    self._digit_buttons.append(b)
                elif label == "Ans":
                    b = ctk.CTkButton(rf, text=label, height=50, width=80, corner_radius=10,
                                      command=self._insert_ans_value)
                    b.pack(side="left", padx=4, expand=True, fill="x")
                    self._style_digit_button(b, label)
                    self._digit_buttons.append(b)
                else:
                    b = ctk.CTkButton(rf, text=label, height=50, width=80, corner_radius=10,
                                      command=lambda t=label: self._press_num_key(t))
                    b.pack(side="left", padx=4, expand=True, fill="x")
                    self._style_digit_button(b, label)
                    self._digit_buttons.append(b)

        side = ctk.CTkFrame(self.device, corner_radius=14)
        side.pack(fill="both", padx=20, pady=(0, 12))
        self._history_container = side

        head = ctk.CTkFrame(side, fg_color="transparent")
        head.pack(fill="x", padx=6, pady=(6, 2))
        ctk.CTkLabel(head, text="History").pack(side="left")
        ctk.CTkButton(head, text="Hide", width=64, command=self._toggle_history).pack(side="right")

        body = ctk.CTkFrame(side, fg_color="transparent")
        body.pack(fill="x", padx=6, pady=(0, 6))
        self.hist_list = tk.Listbox(body, height=6, activestyle="dotbox")
        self.hist_list.pack(side="left", fill="x", expand=True)
        sb = tk.Scrollbar(body, orient="vertical", command=self.hist_list.yview)
        self.hist_list.config(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")

        btns = ctk.CTkFrame(side, fg_color="transparent")
        btns.pack(fill="x", padx=6, pady=(0, 6))
        ctk.CTkButton(btns, text="Reuse", width=80, command=self.history_reuse).pack(side="left", padx=2)
        ctk.CTkButton(btns, text="Delete", width=80, command=self.history_delete).pack(side="left", padx=2)
        ctk.CTkButton(btns, text="Clear", width=80, command=self.history_clear).pack(side="left", padx=2)

        self.apply_theme(self._palette, self._theme_name)

    def _open_pet_calc(self):
        app = self.winfo_toplevel()
        if hasattr(app, "open_pet_calculator"):
            try:
                app.open_pet_calculator()
            except Exception:
                pass

    def _handle_pet_single_click(self):
        now = time.time()
        if now - self._pet_last_click_ts > 0.9:
            self._pet_click_count = 0
        self._pet_last_click_ts = now
        self._pet_click_count += 1

        if self._pet_bubble and self._pet_bubble.winfo_exists():
            try:
                self._pet_bubble.destroy()
            except Exception:
                pass
            self._pet_bubble = None

        if self._pet_click_count >= 3:
            self._pet_click_count = 0
            self._open_pet_calc()
            return

        self._pet_bubble = show_cat_bubble(
            self.pet._label,
            "再多点击几次可能会有意想不到的事情发生哦~",
            palette=self._palette,
            direction="left",
            wrap_width=260,
        )
        self._pet_hint_shown = True

    def _move_cursor_left(self, event=None): #光标左移

        entry = self.expr_entry
        entry.focus_set()
        try:
            pos = entry.index("sel.first") if entry.selection_present() else entry.index("insert")
        except:
            pos = entry.index("insert")
        if pos > 0:
            entry.icursor(pos - 1)

    def _move_cursor_right(self, event=None):#光标右移
        entry = self.expr_entry
        entry.focus_set()
        s = entry.get()
        try:
            pos = entry.index("sel.last") if entry.selection_present() else entry.index("insert")
        except:
            pos = entry.index("insert")
            if pos < len(s):
                entry.icursor(pos + 1)


                    # ---- Styles/helpers ------------------------------------------------------
    def _style_func_button(self, b, kind, enabled=True):
        pal = self._palette
        if not enabled or kind == "ghost":
            b.configure(state="disabled", fg_color=pal.get("func", "#9AA1A8"),
                        text_color=pal.get("subtext", "#6C6C70"),
                        border_width=1, border_color=pal.get("func_border", "#8A9299"))
            return
        b.configure(fg_color=pal.get("func", "#9AA1A8"),
                    hover_color=pal.get("func_hover", "#8F969E"),
                    text_color=pal.get("text", "#000000"),
                    border_width=1, border_color=pal.get("func_border", "#8A9299"))

    def _style_digit_button(self, b, label):
        pal = self._palette
        b.configure(fg_color=pal.get("digit", "#FFFFFF"),
                    hover_color=pal.get("digit_hover", "#F2F2F7"),
                    text_color=pal.get("digit_text", "#222222"),
                    border_width=1, border_color=pal.get("digit_border", "#D6D7DA"))

    def _style_op_button(self, b, kind):
        pal = self._palette
        if kind == "accent":
            b.configure(fg_color=pal.get("blue", "#3F8CFF"),
                        hover_color=pal.get("blue", "#3F8CFF"),
                        text_color=pal.get("accent_text", "#FFFFFF"),
                        border_width=0)
        elif kind == "equal":
            b.configure(fg_color=pal.get("orange", "#E67E36"),
                        hover_color=pal.get("orange", "#E67E36"),
                        text_color=pal.get("accent_text", "#FFFFFF"),
                        border_width=0)
        else:
            b.configure(fg_color=pal.get("orange_soft", "#E8A26B"),
                        hover_color=pal.get("orange_soft", "#E8A26B"),
                        text_color=pal.get("accent_text", "#FFFFFF"),
                        border_width=0)

    def _press_num_key(self, label):
        self.insert_text(label)

    def _toggle_drg(self):
        self.evaluator.deg_mode = not self.evaluator.deg_mode
        self.mode_lbl.configure(text="D" if self.evaluator.deg_mode else "R")

    def _insert_template(self, template, cursor_offset):
        entry = self.expr_entry
        try:
            if entry.selection_present():
                start = entry.index("sel.first")
                end = entry.index("sel.last")
                entry.delete(start, end)
                pos = start
            else:
                pos = entry.index("insert")
        except Exception:
            pos = entry.index("insert")
        entry.insert(pos, template)
        entry.icursor(pos + cursor_offset)
        entry.focus_set()

    # 通用：包裹或插入并高亮括号内；若有选中内容则包裹，否则插入占位符
    def _insert_or_wrap_select(self, prefix: str, suffix: str, placeholder: str = "x"):
        entry = self.expr_entry
        try:
            if entry.selection_present():
                start = entry.index("sel.first")
                end = entry.index("sel.last")
                content = entry.get()
                inside = content[start:end]
                entry.delete(start, end)
                pos = start
            else:
                pos = entry.index("insert")
                inside = placeholder

            entry.insert(pos, prefix + inside + suffix)
            sel_start = pos + len(prefix)
            sel_end = sel_start + len(inside)
            try:
                entry.selection_range(sel_start, sel_end) #高亮括号内
            except Exception:
                entry.icursor(sel_start)
            entry.focus_set()
        except Exception:
            entry.insert("insert", prefix + suffix)
            try:
                cur = entry.index("insert")
                entry.icursor(cur - len(suffix))
            except Exception:
                pass
            entry.focus_set()

    # 插入函数/结构（包裹并高亮）
    def _insert_sqrt(self):
        self._insert_or_wrap_select("sqrt(", ")")

    def _insert_y_root(self):
        # y√x: root(deg, val)
        entry = self.expr_entry
        try:
            if entry.selection_present():
                start = entry.index("sel.first")
                end = entry.index("sel.last")
                content = entry.get()
                selected = content[start:end]
                entry.delete(start, end)
                pos = start
                text = f"root(n, {selected})"
                entry.insert(pos, text)
                sel_start = pos + len("root(")
                sel_end = sel_start + 1
                try:
                    entry.selection_range(sel_start, sel_end)
                except Exception:
                    entry.icursor(sel_start)
                entry.focus_set()
            else:
                pos = entry.index("insert")
                entry.insert(pos, "root(, )")
                sel_start = pos + len("root(")
                sel_end = sel_start + 1
                try:
                    entry.selection_range(sel_start, sel_end)
                except Exception:
                    entry.icursor(sel_start)
                entry.focus_set()
        except Exception:
            pos = entry.index("insert")
            entry.insert(pos, "root(, )")
            sel_start = pos + len("root(")
            sel_end = sel_start + 1
            try:
                entry.selection_range(sel_start, sel_end)
            except Exception:
                entry.icursor(sel_start)
            entry.focus_set()

    def _insert_factorial(self):
        self._insert_or_wrap_select("fact(", ")")

    def _insert_abs(self):
        self._insert_or_wrap_select("abs(", ")")

    def _insert_arcsin(self):
        self._insert_or_wrap_select("asin(", ")")

    def _insert_arccos(self):
        self._insert_or_wrap_select("acos(", ")")

    def _insert_arctan(self):
        self._insert_or_wrap_select("atan(", ")")

    def _insert_sin(self):
        self._insert_or_wrap_select("sin(", ")")

    def _insert_cos(self):
        self._insert_or_wrap_select("cos(", ")")

    def _insert_tan(self):
        self._insert_or_wrap_select("tan(", ")")

    def _insert_ln(self):
        self._insert_or_wrap_select("ln(", ")")

    def _insert_log10(self):
        self._insert_or_wrap_select("log10(", ")")

    def _insert_reciprocal(self):
        self._insert_or_wrap_select("1/(", ")")

    def _insert_pow2(self):
        # (base)^2，选中 base
        self._insert_or_wrap_select("(", ")^2")

    def _insert_pow3(self):
        # (base)^3，选中 base
        self._insert_or_wrap_select("(", ")^3")

    def _insert_ten_power(self):
        # 插入 "*10^()" 并高亮括号内
        self._insert_or_wrap_select("*10^(", ")", "x")

    def _insert_ans_value(self):
        value = self.evaluator.last_result
        try:
            numeric = float(value)
            text = self._format_result(numeric)
        except Exception:
            text = str(value)
        if not text:
            text = "0"
        self.insert_text(text)

    def _power_prompt(self):
        parent = self.winfo_toplevel()
        defaults = self._pow_last_args or {}

        def _ask(prompt, key):
            initial = defaults.get(key, "")
            while True:
                resp = simpledialog.askstring("xⁿ", prompt, initialvalue=initial, parent=parent)
                if resp is None:
                    return None
                resp = resp.strip()
                if not resp:
                    messagebox.showerror("xⁿ", "输入不能为空", parent=parent)
                    continue
                return resp

        base_text = _ask("底数 =", "base")
        if base_text is None:
            return
        try:
            base_val = self._eval_numeric(base_text, {})
        except Exception as exc:
            messagebox.showerror("xⁿ", f"底数无效: {exc}", parent=parent)
            return

        exp_text = _ask("指数 =", "exp")
        if exp_text is None:
            return
        try:
            exp_val = self._eval_numeric(exp_text, {})
        except Exception as exc:
            messagebox.showerror("xⁿ", f"指数无效: {exc}", parent=parent)
            return

        try:
            result = base_val ** exp_val
        except Exception as exc:
            messagebox.showerror("xⁿ", f"计算失败: {exc}", parent=parent)
            return

        try:
            result_float = float(result)
        except Exception:
            messagebox.showerror("xⁿ", "结果不是实数", parent=parent)
            return
        if not math.isfinite(result_float):
            messagebox.showerror("xⁿ", "结果不是有限数", parent=parent)
            return

        formatted = self._format_result(result_float)
        expr_display = f"({base_text})^({exp_text})"
        self.expr_var.set(expr_display)
        self.result_var.set(formatted)
        self.mode_lbl.configure(text=("D" if self.evaluator.deg_mode else "R"))
        self._add_history(expr_display, formatted)
        self._pow_last_args = {"base": base_text, "exp": exp_text}
        try:
            self.evaluator.last_result = result_float
        except Exception:
            pass
        play_sound("assets/cat.mp3")

    def _integral_prompt(self):
        parent = self.winfo_toplevel()
        defaults = self._integral_last_args or {}

        def _ask(prompt, key):
            initial = defaults.get(key, "")
            while True:
                resp = simpledialog.askstring("∫", prompt, initialvalue=initial, parent=parent)
                if resp is None:
                    return None
                resp = resp.strip()
                if not resp:
                    messagebox.showerror("∫", "输入不能为空", parent=parent)
                    continue
                return resp

        var_name = _ask("积分变量 (如 x):", "var")
        if var_name is None:
            return
        if not var_name.isidentifier():
            messagebox.showerror("∫", "变量名称无效", parent=parent)
            return

        lower_expr = _ask(f"{var_name} 的下限:", "lower")
        if lower_expr is None:
            return
        upper_expr = _ask(f"{var_name} 的上限:", "upper")
        if upper_expr is None:
            return

        try:
            lower_val = self._eval_numeric(lower_expr, {})
        except Exception as exc:
            messagebox.showerror("∫", f"下限无效: {exc}", parent=parent)
            return
        try:
            upper_val = self._eval_numeric(upper_expr, {})
        except Exception as exc:
            messagebox.showerror("∫", f"上限无效: {exc}", parent=parent)
            return
        try:
            lower = float(lower_val)
            upper = float(upper_val)
        except Exception:
            messagebox.showerror("∫", "上下限必须是实数", parent=parent)
            return

        expr_text = _ask(f"被积函数关于 {var_name}:", "expr")
        if expr_text is None:
            return

        def integrate(expr_string, var, a, b):
            if math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12):
                return 0.0
            sign = 1.0
            if a > b:
                a, b = b, a
                sign = -1.0
            cache = {}

            def f(x):
                if x in cache:
                    return cache[x]
                val = self._eval_numeric(expr_string, {var: x})
                try:
                    val = float(val)
                except Exception:
                    raise ValueError("积分过程中出现无法转换的数值")
                if not math.isfinite(val):
                    raise ValueError("积分过程中出现非有限值")
                cache[x] = val
                return val

            def simpson(a_, b_):
                c = 0.5 * (a_ + b_)
                return (b_ - a_) / 6.0 * (f(a_) + 4.0 * f(c) + f(b_))

            def recurse(a_, b_, eps, whole, depth):
                c = 0.5 * (a_ + b_)
                left = simpson(a_, c)
                right = simpson(c, b_)
                delta = left + right - whole
                if depth <= 0 or abs(delta) <= 15 * eps:
                    return left + right + delta / 15.0
                return recurse(a_, c, eps / 2.0, left, depth - 1) + recurse(c, b_, eps / 2.0, right, depth - 1)

            try:
                whole = simpson(a, b)
                result = recurse(a, b, 1e-7, whole, 12)
            except RecursionError as exc:
                raise ValueError(f"积分失败: {exc}")
            return sign * result

        try:
            integral_value = integrate(expr_text, var_name, lower, upper)
        except ValueError as exc:
            messagebox.showerror("∫", str(exc), parent=parent)
            return
        except Exception as exc:
            messagebox.showerror("∫", f"积分失败: {exc}", parent=parent)
            return

        formatted = self._format_result(integral_value)
        display_expr = f"∫[{lower_expr},{upper_expr}] {expr_text} d{var_name}"
        self.expr_var.set(display_expr)
        self.result_var.set(formatted)
        self.mode_lbl.configure(text=("D" if self.evaluator.deg_mode else "R"))

        self._add_history(display_expr, formatted)
        self._integral_last_args = {"var": var_name, "lower": lower_expr, "upper": upper_expr, "expr": expr_text}
        try:
            self.evaluator.last_result = float(integral_value)
        except Exception:
            pass
        play_sound("assets/cat.mp3")

    def _derivative_prompt(self):
        expr = self.expr_var.get().strip()
        if not expr:
            messagebox.showerror("d/dx", "请先输入要求导的函数", parent=self.winfo_toplevel())
            return

        parent = self.winfo_toplevel()
        var_input = simpledialog.askstring("d/dx", "对哪个变量求导？", initialvalue=self._derivative_last_var, parent=parent)
        if var_input is None:
            return
        var_name = var_input.strip() or self._derivative_last_var
        if not var_name.isidentifier():
            messagebox.showerror("d/dx", "变量名称无效", parent=parent)
            return

        try:
            import sympy as sp
        except Exception:
            messagebox.showerror("d/dx", "需要安装 sympy 才能使用求导功能", parent=parent)
            return

        expr_processed = self.evaluator._preprocess(expr)
        last_ans = float(self.evaluator.last_result) if isinstance(self.evaluator.last_result, (int, float)) else 0.0
        sym_var = sp.symbols(var_name)

        def log10_fn(x):
            return sp.log(x, 10)

        def root_fn(deg, val):
            try:
                return val ** (sp.Integer(1) / deg)
            except Exception:
                return val ** (1 / deg)

        locals_dict = {
            var_name: sym_var,
            "pi": sp.pi,
            "e": sp.E,
            "Ans": sp.Float(last_ans),
            "sin": sp.sin,
            "cos": sp.cos,
            "tan": sp.tan,
            "asin": sp.asin,
            "acos": sp.acos,
            "atan": sp.atan,
            "arcsin": sp.asin,
            "arccos": sp.acos,
            "arctan": sp.atan,
            "sqrt": sp.sqrt,
            "abs": sp.Abs,
            "log": sp.log,
            "ln": sp.log,
            "log10": log10_fn,
            "exp": sp.exp,
            "pow": sp.Pow,
            "root": root_fn,
            "yroot": root_fn,
            "nthroot": root_fn,
            "fact": sp.factorial,
            "factorial": sp.factorial,
        }

        try:
            sym_expr = sp.sympify(expr_processed, locals=locals_dict)
        except Exception as exc:
            messagebox.showerror("d/dx", f"无法解析表达式: {exc}", parent=parent)
            return

        try:
            deriv_expr = sp.diff(sym_expr, sym_var)
            deriv_simplified = sp.simplify(deriv_expr)
        except Exception as exc:
            messagebox.showerror("d/dx", f"求导失败: {exc}", parent=parent)
            return

        deriv_text = sp.sstr(deriv_simplified)
        display_expr = f"d/d{var_name}({expr})"
        self.expr_var.set(display_expr)
        self.result_var.set(deriv_text)
        self.mode_lbl.configure(text=("D" if self.evaluator.deg_mode else "R"))

        self._add_history(display_expr, deriv_text)
        self._derivative_last_var = var_name
        play_sound("assets/cat.mp3")

    def _evaluate_with_context(self, expr, context):
        saved_ans = self.evaluator.last_result
        try:
            return self.evaluator.evaluate(expr, context)
        finally:
            self.evaluator.last_result = saved_ans

    def _eval_numeric(self, expr, context):
        value = self._evaluate_with_context(expr, context)
        if isinstance(value, bool):
            value = float(value)
        if not isinstance(value, (int, float)):
            raise ValueError("结果不是数值")
        value = float(value)
        if not math.isfinite(value):
            raise ValueError("结果不是有限数")
        return value

    def _extract_variables(self, expr):
        processed = self.evaluator._preprocess(expr)
        try:
            tree = ast.parse(processed, mode="eval")
        except Exception as exc:
            raise ValueError(f"表达式错误: {exc}")

        allowed = set(self.evaluator._allowed_names().keys())
        names = []
        seen = set()

        class Visitor(ast.NodeVisitor):
            def visit_Name(self, node):
                if node.id in allowed:
                    return
                if node.id not in seen:
                    seen.add(node.id)
                    names.append(node.id)

        Visitor().visit(tree)
        return names

    def _prompt_for_variables(self, var_names, *, title, defaults=None):
        defaults = defaults or {}
        values = {}
        parent = self.winfo_toplevel()
        for name in var_names:
            initial = defaults.get(name)
            initial_text = "" if initial is None else self._format_result(initial)
            while True:
                answer = simpledialog.askstring(title, f"{name} = ?", initialvalue=initial_text, parent=parent)
                if answer is None:
                    return None
                answer = answer.strip()
                if not answer:
                    messagebox.showerror(title, f"{name} 不能为空", parent=parent)
                    continue
                try:
                    value = self._eval_numeric(answer, {**values})
                except Exception as exc:
                    messagebox.showerror(title, f"{name} 输入无效: {exc}", parent=parent)
                    continue
                values[name] = value
                break
        return values

    def _sigma_sum(self):
        parent = self.winfo_toplevel()
        defaults = self._sigma_last_args or {}

        def _ask(prompt, key):
            initial = defaults.get(key, "")
            while True:
                answer = simpledialog.askstring("Σ", prompt, initialvalue=initial, parent=parent)
                if answer is None:
                    return None
                answer = answer.strip()
                if not answer:
                    messagebox.showerror("Σ", "输入不能为空", parent=parent)
                    continue
                return answer

        var_name = _ask("下标变量 (如 n):", "var")
        if var_name is None:
            return
        if not var_name.isidentifier():
            messagebox.showerror("Σ", "下标变量必须是有效的名称", parent=parent)
            return

        lower_expr = _ask(f"{var_name} 的下限:", "lower")
        if lower_expr is None:
            return
        try:
            lower_val = self._eval_numeric(lower_expr, {})
        except Exception as exc:
            messagebox.showerror("Σ", f"下限无效: {exc}", parent=parent)
            return
        lower_int = int(round(lower_val))
        if not math.isclose(lower_val, lower_int, rel_tol=1e-9, abs_tol=1e-9):
            messagebox.showerror("Σ", "下限必须为整数", parent=parent)
            return

        upper_expr = _ask(f"{var_name} 的上限:", "upper")
        if upper_expr is None:
            return
        try:
            upper_val = self._eval_numeric(upper_expr, {})
        except Exception as exc:
            messagebox.showerror("Σ", f"上限无效: {exc}", parent=parent)
            return
        upper_int = int(round(upper_val))
        if not math.isclose(upper_val, upper_int, rel_tol=1e-9, abs_tol=1e-9):
            messagebox.showerror("Σ", "上限必须为整数", parent=parent)
            return
        if upper_int < lower_int:
            messagebox.showerror("Σ", "上限必须不小于下限", parent=parent)
            return

        expr_text = _ask(f"输入关于 {var_name} 的表达式:", "expr")
        if expr_text is None:
            return

        total = 0.0
        for i in range(lower_int, upper_int + 1):
            try:
                term = self._eval_numeric(expr_text, {var_name: i})
            except Exception as exc:
                messagebox.showerror("Σ", f"计算第 {i} 项时出错: {exc}", parent=parent)
                return
            total += term

        formatted = self._format_result(total)
        display_expr = f"Σ({var_name}={lower_int}..{upper_int}) {expr_text}"
        self.expr_var.set(display_expr)
        self.result_var.set(formatted)
        self.mode_lbl.configure(text=("D" if self.evaluator.deg_mode else "R"))

        hist_expr = f"Σ {var_name} of {expr_text}"
        self._add_history(hist_expr, formatted)

        self._sigma_last_args = {"var": var_name, "lower": lower_expr, "upper": upper_expr, "expr": expr_text}
        try:
            self.evaluator.last_result = float(total)
        except Exception:
            pass

        play_sound("assets/cat.mp3")

    def _generate_initial_guesses(self):
        guesses = []
        if self._solve_last_guess is not None and math.isfinite(self._solve_last_guess):
            guesses.append(float(self._solve_last_guess))
        ans = self.evaluator.last_result
        if isinstance(ans, (int, float)):
            ans_val = float(ans)
            if math.isfinite(ans_val):
                guesses.append(ans_val)
        guesses.extend([0.0, 1.0, -1.0, 2.0, -2.0, 5.0, -5.0, 10.0, -10.0])
        unique = []
        seen = set()
        for g in guesses:
            if not isinstance(g, (int, float)):
                continue
            g_val = float(g)
            if not math.isfinite(g_val):
                continue
            key = round(g_val, 12)
            if key in seen:
                continue
            seen.add(key)
            unique.append(g_val)
        if not unique:
            unique.append(0.0)
        return unique

    def _calc_expression(self):
        expr = self.expr_var.get().strip()
        if not expr:
            return
        target_expr = expr.split("=", 1)[0].strip() if "=" in expr else expr
        if not target_expr:
            messagebox.showerror("CALC", "请输入表达式", parent=self.winfo_toplevel())
            return
        try:
            variables = self._extract_variables(target_expr)
        except ValueError as exc:
            messagebox.showerror("CALC", str(exc), parent=self.winfo_toplevel())
            return
        if not variables:
            self.calculate()
            return
        defaults = {name: self._calc_last_values.get(name) for name in variables if name in self._calc_last_values}
        values = self._prompt_for_variables(variables, title="CALC", defaults=defaults)
        if values is None:
            return
        try:
            result = self.evaluator.evaluate(target_expr, values)
        except Exception as exc:
            messagebox.showerror("CALC", f"计算失败: {exc}", parent=self.winfo_toplevel())
            return
        formatted = self._format_result(result)
        self.result_var.set(formatted)
        self.mode_lbl.configure(text=("D" if self.evaluator.deg_mode else "R"))
        assigns = ", ".join(f"{name}={self._format_result(values[name])}" for name in variables)
        hist_expr = f"CALC {target_expr}"
        if assigns:
            hist_expr += f" | {assigns}"
        self._add_history(hist_expr, formatted)
        self._calc_last_values = dict(values)
        play_sound("assets/cat.mp3")

    def _normalize_equation(self, expr):
        if "=" not in expr:
            return expr
        parts = expr.split("=")
        if len(parts) != 2:
            raise ValueError("仅支持包含单个 '=' 的方程")
        left, right = parts
        if not left.strip() or not right.strip():
            raise ValueError("方程两侧不能为空")
        return f"({left.strip()})-({right.strip()})"

    def _choose_solve_variable(self, variables):
        if not variables:
            return None
        parent = self.winfo_toplevel()
        preferred = None
        for candidate in ("x", "y"):
            if candidate in variables:
                preferred = candidate
                break
        if preferred is None:
            preferred = variables[0]
        if len(variables) == 1:
            self._solve_last_var = variables[0]
            return variables[0]
        initial = self._solve_last_var if self._solve_last_var in variables else preferred
        while True:
            choice = simpledialog.askstring(
                "SOLVE",
                f"选择未知数 ({', '.join(variables)})",
                initialvalue=initial,
                parent=parent,
            )
            if choice is None:
                return None
            choice = choice.strip()
            if choice in variables:
                self._solve_last_var = choice
                return choice
            messagebox.showerror("SOLVE", "未知数名称不在表达式中", parent=parent)

    def _solve_equation(self):
        expr = self.expr_var.get().strip()
        if not expr:
            return
        try:
            normalized = self._normalize_equation(expr)
        except ValueError as exc:
            messagebox.showerror("SOLVE", str(exc), parent=self.winfo_toplevel())
            return
        try:
            variables = self._extract_variables(normalized)
        except ValueError as exc:
            messagebox.showerror("SOLVE", str(exc), parent=self.winfo_toplevel())
            return
        if not variables:
            messagebox.showerror("SOLVE", "方程中没有未知数", parent=self.winfo_toplevel())
            return

        target = self._choose_solve_variable(variables)
        if not target:
            return

        param_names = [name for name in variables if name != target]
        if self._solve_last_var != target:
            self._solve_last_guess = None
            self._solve_last_params = {}

        params = {}
        if param_names:
            params = self._prompt_for_variables(
                param_names,
                title="SOLVE",
                defaults={k: self._solve_last_params.get(k) for k in param_names},
            )
            if params is None:
                return

        tol_f = 1e-9
        tol_x = 1e-9

        def func(value):
            try:
                return self._eval_numeric(normalized, {**params, target: value})
            except Exception as exc:
                raise ValueError(exc)

        def try_newton(x0):
            x = x0
            for _ in range(40):
                try:
                    fx = func(x)
                except ValueError:
                    break
                if abs(fx) < tol_f:
                    return x
                h = max(1e-6, abs(x) * 1e-6)
                try:
                    fp = func(x + h)
                    fm = func(x - h)
                except ValueError:
                    break
                denom = fp - fm
                if abs(denom) < 1e-12:
                    break
                dfx = denom / (2 * h)
                if not math.isfinite(dfx) or abs(dfx) < 1e-12:
                    break
                x_next = x - fx / dfx
                if not math.isfinite(x_next):
                    break
                if abs(x_next - x) < max(tol_x, abs(x_next) * tol_x):
                    try:
                        if abs(func(x_next)) < tol_f:
                            return x_next
                    except ValueError:
                        return None
                x = x_next
            return None

        def find_bracket(x0):
            step = max(1.0, abs(x0) * 0.5)
            left = x0 - step
            right = x0 + step
            for _ in range(32):
                fa = fb = None
                try:
                    fa = func(left)
                except ValueError:
                    pass
                try:
                    fb = func(right)
                except ValueError:
                    pass
                if fa is not None and abs(fa) < tol_f:
                    return left, left
                if fb is not None and abs(fb) < tol_f:
                    return right, right
                if fa is not None and fb is not None and fa * fb < 0:
                    return left, right
                step *= 1.6
                left = x0 - step
                right = x0 + step
            return None

        def bisect(a, b):
            try:
                fa = func(a)
                fb = func(b)
            except ValueError as exc:
                raise exc
            if fa == 0:
                return a
            if fb == 0:
                return b
            if fa * fb > 0:
                raise ValueError("未找到有效的区间")
            x_left, x_right = a, b
            f_left, f_right = fa, fb
            for _ in range(80):
                mid = 0.5 * (x_left + x_right)
                fm = func(mid)
                if abs(fm) < tol_f or abs(x_right - x_left) < max(tol_x, abs(mid) * tol_x):
                    return mid
                if f_left * fm <= 0:
                    x_right, f_right = mid, fm
                else:
                    x_left, f_left = mid, fm
            return 0.5 * (x_left + x_right)

        root = None
        candidates = self._generate_initial_guesses()
        for guess in candidates:
            candidate_root = try_newton(guess)
            if candidate_root is None:
                bracket = find_bracket(guess)
                if bracket:
                    if math.isclose(bracket[0], bracket[1], abs_tol=tol_x):
                        candidate_root = bracket[0]
                    else:
                        try:
                            candidate_root = bisect(*bracket)
                        except Exception:
                            candidate_root = None
            if candidate_root is not None and math.isfinite(candidate_root):
                root = candidate_root
                break

        if root is None:
            messagebox.showerror("SOLVE", "未找到解，请调整表达式或参数", parent=self.winfo_toplevel())
            return

        if root is None or not math.isfinite(root):
            messagebox.showerror("SOLVE", "求解失败，请调整表达式或参数", parent=self.winfo_toplevel())
            return

        try:
            residual = func(root)
        except Exception:
            residual = float("inf")

        if not math.isfinite(residual):
            messagebox.showerror("SOLVE", "求解结果不收敛，请调整表达式或参数", parent=self.winfo_toplevel())
            return

        formatted = self._format_result(root)
        self.result_var.set(formatted)
        self.mode_lbl.configure(text=("D" if self.evaluator.deg_mode else "R"))

        param_desc = ", ".join(f"{name}={self._format_result(params[name])}" for name in param_names)
        hist_expr = f"SOLVE {expr}"
        if param_desc:
            hist_expr += f" | {param_desc}"
        self._add_history(hist_expr, f"{target} = {formatted}")

        self._solve_last_guess = root
        self._solve_last_params = dict(params)
        self._solve_last_var = target
        self.evaluator.last_result = float(root)

        play_sound("assets/cat.mp3")

    # ---- Calculator logic ----------------------------------------------------
    def insert_text(self, text):
        if not text:
            return
        self.expr_entry.insert("insert", text)
        self.expr_entry.focus_set()

    def clear_expr(self):
        self.expr_var.set("")
        self.result_var.set("0")

    def backspace(self):
        s = self.expr_var.get()
        if s:
            self.expr_var.set(s[:-1])

    def calculate(self):
        expr = self.expr_var.get().strip()
        if not expr:
            return
        try:
            res = self.evaluator.evaluate(expr)
            formatted = self._format_result(res)
            self.result_var.set(formatted)
            self.mode_lbl.configure(text=("D" if self.evaluator.deg_mode else "R"))
            self._add_history(expr, formatted)

            play_sound("assets/cat.mp3")

        except Exception as e:
            self.result_var.set(f"Error: {e}")

    def _format_result(self, value):
        if isinstance(value, float):
            if not math.isfinite(value):
                return str(value)
            text = format(value, ".12g")
            if "e" not in text and "." in text:
                text = text.rstrip("0").rstrip(".")
            if text == "-0":
                text = "0"
            return text
        return str(value)

    def _add_history(self, expr, res):
        self.history.append({"expr": expr, "result": res})
        self.hist_list.insert("end", f"{expr} = {res}")
        if self.hist_list.size() > 500:
            self.hist_list.delete(0)

    def history_reuse(self):
        sel = self.hist_list.curselection()
        if sel:
            self.expr_var.set(self.history[sel[0]]["expr"])

    def history_delete(self):
        sel = self.hist_list.curselection()
        if sel:
            idx = sel[0]
            self.hist_list.delete(idx)
            del self.history[idx]

    def history_clear(self):
        self.hist_list.delete(0, "end")
        self.history.clear()

    def _toggle_history(self):
        cont = getattr(self, "_history_container", None)
        if not cont:
            return
        if cont.winfo_manager():
            cont.pack_forget()
        else:
            cont.pack(fill="both", padx=20, pady=(0, 12))

    def _toggle_mute(self):
        try:
            toggle_muted()
        except Exception:
            pass
        self._sync_mute_btn()

    def _sync_mute_btn(self):
        try:
            self._mute_btn.configure(text=("切换成有声" if is_muted() else "切换成无声"))
        except Exception:
            pass

    def apply_theme(self, pal, name):
        self._palette = pal
        self._theme_name = name

        try:
            self.device.configure(fg_color=pal.get("device", "#C8CDD2"))
        except Exception:
            pass

        self.lbl_brand.configure(text_color=pal.get("text", "#000"))
        self.lbl_sub.configure(text_color=pal.get("subtext", "#6C6C70"))
        self.res_lbl.configure(text_color=pal.get("text", "#000"))
        self.mode_lbl.configure(text_color=pal.get("subtext", "#6C6C70"))

        try:
            self.hist_list.configure(
                bg=pal.get("surface", "#FFFFFF"),
                fg=pal.get("text", "#000000"),
                selectbackground="#DCEBFF" if name != "iOS Dark" else "#133E7C",
                highlightthickness=1, highlightbackground=pal.get("border", "#C6C6C8"),
                relief="flat", bd=1
            )
        except Exception:
            pass

        for b, kind, enabled in self._func_buttons:
            self._style_func_button(b, kind=kind, enabled=enabled)
        for b in self._digit_buttons:
            self._style_digit_button(b, "")
        for b, kind in self._op_buttons:
            self._style_op_button(b, kind=kind)

        for lbl in getattr(self, "_circle_labels", []):
            try:
                lbl.configure(text_color=pal.get("subtext", "#6C6C70"))
            except Exception:
                pass

        try:
            if getattr(self, "_circle_middle_lbl", None) and self._circle_middle_d:
                color = pal.get("subtext", "#6C6C70")
                img = self._make_circle_x_image(self._circle_middle_d, color)
                self._circle_middle_lbl.configure(image=img, text="")
                self._circle_middle_img = img
        except Exception:
            pass
        self._sync_mute_btn()










