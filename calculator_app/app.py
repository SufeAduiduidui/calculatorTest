import math
import tkinter as tk
import customtkinter as ctk #ctk库，优化ui～ ctk开不需要太多的css或其他复杂配置，就可以制作出美观的界面

from .core.safe_eval import SafeEvaluator
from .ui.calculator_page import CalculatorPage
from .ui.convert_page import ConvertPage
from .ui.plot_page import PlotPage
from .ui.theme import palette_for

#主应用GUI
class CalculatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Scientific Calculator")

        self.geometry("980x640")#在macos上好像有点问题

        self.minsize(900, 840)
        ctk.set_appearance_mode("Light")#默认浅色主题
        ctk.set_default_color_theme("blue")
        self.evaluator = SafeEvaluator(deg_mode=False)#默认弧度制
        self.history = []
        self.theme_var = tk.StringVar(value="iOS Light")
        self.page_var = tk.StringVar(value="calc")
        # Initialize palette early to avoid KeyError during widget styling
        self._palette = palette_for("iOS Light")

        self._build_navbar()
        self._build_pages()

        self.calc_page = CalculatorPage(self.calc_frame, evaluator=self.evaluator, palette=self._palette, theme_name=self.theme_var.get())
        self.conv_page = ConvertPage(self.conv_frame)
        self.plot_page = PlotPage(self.plot_frame, evaluator=self.evaluator, palette=self._palette, theme_name=self.theme_var.get())
        self.calc_page.pack(fill="both", expand=True)
        self.conv_page.pack(fill="both", expand=True)
        self.plot_page.pack(fill="both", expand=True)

        self.apply_theme("iOS Light")
        self._show_page("calc")

#ui配色
    # 顶层使用独立模块函数 palette_for(name)

#顶部导航栏
    def _build_navbar(self):
        bar = ctk.CTkFrame(self, corner_radius=12)
        bar.pack(side="top", fill="x", padx=10, pady=(10, 6))

        left = ctk.CTkFrame(bar, fg_color="transparent")
        left.pack(side="left", padx=6, pady=8)

        self.page_seg = ctk.CTkSegmentedButton(
            left,
            values=["Calculator", "Convert", "Plot"],
            command=lambda v: self._show_page({"Calculator":"calc", "Convert":"conv", "Plot":"plot"}[v]),
        )
        self.page_seg.set("Calculator")
        self.page_seg.pack(side="left", padx=6)

        right = ctk.CTkFrame(bar, fg_color="transparent")
        right.pack(side="right", padx=6, pady=8)

        self.theme_seg = ctk.CTkSegmentedButton(
            right,
            values=["System", "iOS Light", "iOS Dark"],
            command=self.apply_theme,
        )
        self.theme_seg.set("iOS Light")
        self.theme_seg.pack(side="right", padx=6)

    # ---- Page Container ------------------------------------------------------
    def _build_pages(self):
        body = ctk.CTkFrame(self, corner_radius=12)
        body.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.body = body

        self.calc_frame = ctk.CTkFrame(body, corner_radius=12)
        self.conv_frame = ctk.CTkFrame(body, corner_radius=12)
        self.plot_frame = ctk.CTkFrame(body, corner_radius=12)

    def _show_page(self, key):
        self.page_var.set(key)
        for f in (self.calc_frame, self.conv_frame, self.plot_frame):
            f.pack_forget()
        if key == "calc":
            self.calc_frame.pack(fill="both", expand=True, padx=8, pady=8)
            self.page_seg.set("Calculator")
        elif key == "conv":
            self.conv_frame.pack(fill="both", expand=True, padx=8, pady=8)
            self.page_seg.set("Convert")
        else:
            self.plot_frame.pack(fill="both", expand=True, padx=8, pady=8)
            self.page_seg.set("Plot")

    def apply_theme(self, name):
        self.theme_var.set(name)

        def broadcast(pal, eff):
            self._palette = pal
            self.configure(fg_color=pal.get("bg", "#F5F5F5"))
            try:
                self.body.configure(fg_color=pal.get("bg", "#F5F5F5"))
                self.calc_frame.configure(fg_color=pal.get("bg", "#F5F5F5"))
                self.conv_frame.configure(fg_color=pal.get("bg", "#F5F5F5"))
                self.plot_frame.configure(fg_color=pal.get("bg", "#F5F5F5"))
            except Exception:
                pass
            for seg in (self.page_seg, self.theme_seg):
                try:
                    seg.configure(
                        fg_color=pal.get("surface", "#FFFFFF"),
                        selected_color=pal.get("accent", "#007AFF"),
                        selected_text_color=pal.get("accent_text", "#FFFFFF"),
                        unselected_color=pal.get("surface", "#FFFFFF"),
                    )
                except Exception:
                    pass
            try:
                self.calc_page.apply_theme(pal, eff)
            except Exception:
                pass
            try:
                self.plot_page.apply_theme(pal, eff)
            except Exception:
                pass
            try:
                self.conv_page.apply_theme(pal, eff)
            except Exception:
                pass

        if name == "iOS Dark":
            ctk.set_appearance_mode("Dark")
            eff = "iOS Dark"
            pal = palette_for(eff)
            broadcast(pal, eff)
            return
        if name == "iOS Light":
            ctk.set_appearance_mode("Light")
            eff = "iOS Light"
            pal = palette_for(eff)
            broadcast(pal, eff)
            return

        ctk.set_appearance_mode("System")

        def apply_from_system():
            mode = ctk.get_appearance_mode()
            eff = "iOS Dark" if str(mode).lower() == "dark" else "iOS Light"
            pal = palette_for(eff)
            broadcast(pal, eff)

        self.after(0, apply_from_system)
        apply_from_system()
