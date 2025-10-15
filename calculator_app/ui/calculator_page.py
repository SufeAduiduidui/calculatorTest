import time
import tkinter as tk
import customtkinter as ctk

from .pet_widget import PetWidget  # 桌宠
from ..core.safe_eval import SafeEvaluator

from .sound_player import play as play_sound
from .dialogs import show_cat_bubble


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
        self._build()

    # ---- Calculator (ClassWiz-like) -----------------------------------------
    def _build(self):
        frame = self

        self.device = ctk.CTkFrame(frame, corner_radius=24)
        self.device.pack(fill="both", expand=True, padx=40, pady=20)

        brand = ctk.CTkFrame(self.device, fg_color="transparent")
        brand.pack(side="top", fill="x", padx=20, pady=(18, 6))

        left = ctk.CTkFrame(brand, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True)

        right = ctk.CTkFrame(brand, fg_color="transparent")
        right.pack(side="right")

        self.lbl_brand = ctk.CTkLabel(left, text="CASIO", font=("SF Pro Display", 18, "bold"))
        self.lbl_sub = ctk.CTkLabel(left, text="CLASSWIZ", font=("SF Pro Text", 12))
        self.lbl_brand.pack()
        self.lbl_sub.pack()


        self.pet = PetWidget(
            right,
            image_path="assets/pet.jpg",
            size=(64, 64),
            on_click=self._handle_pet_single_click,
            on_triple_click=self._open_pet_calc,
        )
        self.pet.pack(padx=6, pady=0)


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

        self.result_var = tk.StringVar(value="0")
        self.res_lbl = ctk.CTkLabel(screen, textvariable=self.result_var, anchor="e", font=("Consolas", 28))
        self.res_lbl.pack(fill="x", padx=10, pady=(0, 8))

        func_area = ctk.CTkFrame(self.device, corner_radius=14)
        func_area.pack(fill="x", padx=20, pady=(0, 8))

        funcs = [
            [("SOLVE", None, "ghost", False), ("CALC", None, "ghost", False),
             ("OPTN", None, "ghost", False), ("x^3", "**3", "func", True), ("x^2", "**2", "func", True)],

            [("sqrt", "sqrt(", "func", True), ("y√x", self._insert_y_root, "func_call", True),
             ("1/x", "1/(", "func", True), ("log10", "log10(", "func", True), ("ln", "ln(", "func", True)],

            [("(-)", "-", "func", True), ("\u03C0", "pi", "func", True),
             ("e", "e", "func", True), ("sin", "sin(", "func", True), ("cos", "cos(", "func", True)],

            [("tan", "tan(", "func", True), ("DRG", self._toggle_drg, "func_call", True),
             ("AC", self.clear_expr, "func_call", True), ("(", "(", "func", True), (")", ")", "func", True)],
        ]

        for row in funcs:
            rf = ctk.CTkFrame(func_area, fg_color="transparent")
            rf.pack(fill="x", padx=6, pady=4)
            for text, action, kind, enabled in row:
                if kind == "func_call":
                    cmd = action if enabled else None
                else:
                    cmd = (lambda s=action: self.insert_text(s)) if (enabled and isinstance(action, str)) else None
                b = ctk.CTkButton(rf, text=text, height=36, width=72, corner_radius=10, command=cmd)
                b.pack(side="left", padx=4)
                self._style_func_button(b, kind="func" if enabled else "ghost", enabled=enabled)
                self._func_buttons.append((b, "func" if enabled else "ghost", enabled))

        keypad = ctk.CTkFrame(self.device, corner_radius=14)
        keypad.pack(fill="x", padx=20, pady=(0, 20))

        row_789 = ["7", "8", "9", "DEL", "="]
        row_456 = ["4", "5", "6", "*", "/"]
        row_123 = ["1", "2", "3", "+", "-"]
        row_bottom = ["0", ".", "*10^x", None, None]

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
                    b = ctk.CTkButton(rf, text=label, height=50, width=80, corner_radius=10,
                                      command=lambda: self._press_num_key(label))
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
        if label == "*10^x":
            self.insert_text("*10**(")
        else:
            self.insert_text(label)

    def _toggle_drg(self):
        self.evaluator.deg_mode = not self.evaluator.deg_mode
        self.mode_lbl.configure(text="D" if self.evaluator.deg_mode else "R")

    def _insert_y_root(self):
        self.insert_text("root(")

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
            self.result_var.set(f"{res}")
            self.mode_lbl.configure(text=("D" if self.evaluator.deg_mode else "R"))
            self._add_history(expr, res)

            play_sound("assets/cat.mp3")
            
        except Exception as e:
            self.result_var.set(f"Error: {e}")

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
