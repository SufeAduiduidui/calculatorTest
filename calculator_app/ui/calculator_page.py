import tkinter as tk
from typing import Dict, Tuple
import customtkinter as ctk
import math

class PetCaloriePage(ctk.CTkFrame):
    _CAT_DER_RANGE: dict[str, tuple[float, float]]

    def __init__(self, master, palette=None, theme_name="iOS Light"):
        super().__init__(master, corner_radius=12)
        self._palette = palette or {}
        self._theme_name = theme_name


        self._CAT_DER_RANGE = {
            "发育期": (2.0, 2.5),
            "未结扎": (1.4, 1.6),
            "已结扎": (1.2, 1.4),
            "过胖": (0.8, 1.0),
            "过瘦": (1.2, 1.8),
            "11岁以上高龄": (1.1, 1.6),
        }


        self._BRANDS = {#品牌
            "猫粮": {
                "Orijen Cat&Kitten": 404,
                "Royal Canin Indoor27": 360,
                "Purina Pro Plan": 390,
            },
            "罐头": {
                "希宝金标(85g)": 85,
                "天衡宝(156g)": 110,
            },
            "冻干": {
                "ZIWI Peak": 520,
            },
            "混合": {}
        }

#变量
        self.weight_var = tk.StringVar(value="")
        self.stage_var = tk.StringVar(value="已结扎")
        self.der_var = tk.StringVar(value="")
        self.food_var = tk.StringVar(value="猫粮")
        self.brand_var = tk.StringVar(value="自定义")
        self.kcal_var = tk.StringVar(value="380") #默认猫粮
        self.result_var = tk.StringVar(value="每日建议：- g（- kcal）")
        self.rer_text = tk.StringVar(value="RER：- kcal/日")
        self.der_text = tk.StringVar(value="DER：- kcal/日")

        # DER 范围缓存
        self._der_range = self._CAT_DER_RANGE[self.stage_var.get()]

        self._build()
        self.apply_theme(self._palette, self._theme_name)

#UI--
    def _build(self):
        root = self

        self.device = ctk.CTkFrame(root, corner_radius=24)
        self.device.pack(fill="both", expand=True, padx=40, pady=20)

        top = ctk.CTkFrame(self.device, fg_color="transparent")
        top.pack(side="top", fill="x", padx=20, pady=(16, 8))
        ctk.CTkLabel(top, text="猫咪热量计算器", font=("SF Pro Display", 20, "bold")).pack(side="left")

        card = ctk.CTkFrame(self.device, corner_radius=20)
        card.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self._card = card


        res_row = ctk.CTkFrame(card, fg_color="transparent") # 结果显示
        res_row.pack(fill="x", padx=16, pady=(16, 6))
        res = ctk.CTkEntry(res_row, textvariable=self.result_var, justify="right", state="disabled")
        res.pack(fill="x")


        info_row = ctk.CTkFrame(card, fg_color="transparent")
        info_row.pack(fill="x", padx=16, pady=(2, 8))
        ctk.CTkLabel(info_row, textvariable=self.rer_text).pack(side="left")
        ctk.CTkLabel(info_row, textvariable=self.der_text).pack(side="right")


        w_block = ctk.CTkFrame(card, corner_radius=14)
        w_block.pack(fill="x", padx=16, pady=8)
        ctk.CTkLabel(w_block, text="体重").pack(anchor="w", padx=12, pady=(10, 2))
        w_entry = ctk.CTkEntry(w_block, placeholder_text="单位：kg（例如 4.2）", textvariable=self.weight_var)
        w_entry.pack(fill="x", padx=12, pady=(0, 12))
        self.weight_var.trace_add("write", lambda *_: self._update_preview())


        s_block = ctk.CTkFrame(card, corner_radius=14)
        s_block.pack(fill="x", padx=16, pady=8)
        ctk.CTkLabel(s_block, text="阶段").pack(anchor="w", padx=12, pady=(10, 2))
        s_row = ctk.CTkFrame(s_block, fg_color="transparent")
        s_row.pack(fill="x", padx=12, pady=(0, 12))
        self.stage_menu = ctk.CTkOptionMenu(s_row,
                                            values=list(self._CAT_DER_RANGE.keys()),
                                            command=self._on_stage_change,
                                            variable=self.stage_var)
        self.stage_menu.pack(side="left")
        self.stage_tip = ctk.CTkLabel(s_row, text="")
        self.stage_tip.pack(side="right")


        der_block = ctk.CTkFrame(card, corner_radius=14)
        der_block.pack(fill="x", padx=16, pady=8)
        ctk.CTkLabel(der_block, text="需求因子（DER 系数）").pack(anchor="w", padx=12, pady=(10, 2))
        der_row = ctk.CTkFrame(der_block, fg_color="transparent")
        der_row.pack(fill="x", padx=12, pady=(0, 8))

        self.der_slider = ctk.CTkSlider(der_row, from_=self._der_range[0], to=self._der_range[1],
                                        number_of_steps=20, command=self._on_der_slider)
        self.der_slider.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.der_entry = ctk.CTkEntry(der_row, width=100, textvariable=self.der_var)
        self.der_entry.pack(side="left")
        self.der_entry.bind("<Return>", lambda e: self._on_der_entry_commit())

        self.der_range_lbl = ctk.CTkLabel(der_block, text="")
        self.der_range_lbl.pack(anchor="w", padx=12, pady=(0, 12))


        chips_block = ctk.CTkFrame(card, corner_radius=14)#食物类
        chips_block.pack(fill="x", padx=16, pady=8)
        ctk.CTkLabel(chips_block, text="食物类型").pack(anchor="w", padx=12, pady=(10, 2))
        chips = ctk.CTkFrame(chips_block, fg_color="transparent")
        chips.pack(fill="x", padx=12, pady=(0, 12))
        self._chip_buttons = []
        for label in ["猫粮", "罐头", "冻干", "混合"]:
            btn = ctk.CTkButton(chips, text=label, corner_radius=16, width=80,
                                command=lambda t=label: self._select_food(t))
            btn.pack(side="left", padx=6, pady=6)
            self._chip_buttons.append(btn)



        brand_block = ctk.CTkFrame(card, corner_radius=14)
        brand_block.pack(fill="x", padx=16, pady=8)
        ctk.CTkLabel(brand_block, text="品牌与热量").pack(anchor="w", padx=12, pady=(10, 2))
        br_row = ctk.CTkFrame(brand_block, fg_color="transparent")
        br_row.pack(fill="x", padx=12, pady=(0, 12))
        self.brand_menu = ctk.CTkOptionMenu(br_row,
                                            values=self._brand_values_for(self.food_var.get()),
                                            command=self._on_brand_change,
                                            variable=self.brand_var)
        self.brand_menu.pack(side="left")
        ctk.CTkLabel(br_row, text="kcal/100g").pack(side="right")
        self.kcal_entry = ctk.CTkEntry(br_row, width=120, textvariable=self.kcal_var)
        self.kcal_entry.pack(side="right", padx=(0, 8))

        # 开始计算
        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(fill="x", padx=16, pady=(8, 16))
        self.calc_btn = ctk.CTkButton(btn_row, text="开始计算", command=self._calc)
        self.calc_btn.pack(fill="x")


        self._apply_stage_to_controls()
        self._restyle_chips()

#以下交互
    def _on_stage_change(self, _sel=None):
        stage = self.stage_var.get()
        if stage not in self._CAT_DER_RANGE:
            return
        self._der_range = self._CAT_DER_RANGE[stage]
        self._apply_stage_to_controls()

    def _apply_stage_to_controls(self):
        lo, hi = self._der_range
        mid = round((lo + hi) / 2.0, 2)
        self.der_slider.configure(from_=lo, to=hi)
        self.der_slider.set(mid)
        self.der_var.set(f"{mid:.2f}")
        self.der_range_lbl.configure(text=f"建议范围：{lo:.2f} ～ {hi:.2f}（预设 {mid:.2f}）")
        self.stage_tip.configure(text=f"{self.stage_var.get()} 需求因子")
        self._update_preview()

    def _on_der_slider(self, val):
        self.der_var.set(f"{float(val):.2f}")
        self._update_preview()

    def _on_der_entry_commit(self):
        try:
            v = float(self.der_var.get())
        except Exception:
            return
        lo, hi = self._der_range
        v = max(lo, min(hi, v))
        self.der_var.set(f"{v:.2f}")
        self.der_slider.set(v)
        self._update_preview()

    def _select_food(self, label):
        self.food_var.set(label)
        self._restyle_chips()
        self.brand_menu.configure(values=self._brand_values_for(label))
        self.brand_menu.set("自定义")
        # 典型值
        typical = {"猫粮": 380, "罐头": 100, "冻干": 520, "混合": 300}
        self.kcal_var.set(str(typical.get(label, 350)))
        self._update_preview()

    def _restyle_chips(self):
        pal = self._palette or {}
        sel = self.food_var.get()
        for b in self._chip_buttons:
            if b.cget("text") == sel:
                b.configure(
                    fg_color=pal.get("orange", "#E67E36"),
                    hover_color=pal.get("orange", "#E67E36"),
                    text_color=pal.get("accent_text", "#FFFFFF"),
                    border_width=0
                )
            else:
                b.configure(
                    fg_color=pal.get("func", "#9AA1A8"),
                    hover_color=pal.get("func_hover", "#8F969E"),
                    text_color=pal.get("text", "#000000"),
                    border_width=1, border_color=pal.get("func_border", "#8A9299")
                )

    def _brand_values_for(self, food):
        data = self._BRANDS.get(food, {})
        return ["自定义"] + list(data.keys())

    def _on_brand_change(self, brand_name):
        food = self.food_var.get()
        if brand_name and brand_name != "自定义":
            kc = self._BRANDS.get(food, {}).get(brand_name)
            if kc:
                self.kcal_var.set(str(kc))
        self._update_preview()

    # 计算逻辑 ---------------------------------------------------------------
    @staticmethod
    def _calc_rer(weight_kg: float) -> float:
        # RER = 70 * kg^0.75
        return 70.0 * (weight_kg ** 0.75)

    def _update_preview(self):
        # 轻量更新 RER/DER 预览（不改结果行）
        try:
            w = float(self.weight_var.get())
            w = max(0.0, w)
        except Exception:
            self.rer_text.set("RER：- kcal/日")
            self.der_text.set("DER：- kcal/日")
            return
        try:
            der = float(self.der_var.get())
        except Exception:
            der = None

        if w <= 0:
            self.rer_text.set("RER：- kcal/日")
            self.der_text.set("DER：- kcal/日")
            return

        rer = self._calc_rer(w)
        self.rer_text.set(f"RER：{rer:.0f} kcal/日")
        if der is not None and der > 0:
            self.der_text.set(f"DER：{(rer*der):.0f} kcal/日")
        else:
            self.der_text.set("DER：- kcal/日")

    def _calc(self):
        try:
            w = float(self.weight_var.get())
        except Exception:
            self.result_var.set("请输入你家猫儿or狗儿正确的体重")
            return
        try:
            der = float(self.der_var.get())
        except Exception:
            self.result_var.set("DER系数错误了～")
            return
        try:
            kcal_100g = float(self.kcal_var.get())
        except Exception:
            self.result_var.set("热量错误")
            return

        if w <= 0 or der <= 0 or kcal_100g <= 0:
            self.result_var.set("输入要正数哦")
            return

        rer = self._calc_rer(w)
        der_kcal = rer * der
        grams = der_kcal / kcal_100g * 100.0

        self.rer_text.set(f"RER：{rer:.0f} kcal/日")
        self.der_text.set(f"DER：{der_kcal:.0f} kcal/日")
        self.result_var.set(f"每日建议摄入：{grams:.0f} g（约 {der_kcal:.0f} kcal）")


    def apply_theme(self, pal, name):
        self._palette = pal or {}
        self._theme_name = name
        try:
            self.configure(fg_color=pal.get("bg", "#F5F5F5"))
            self.device.configure(fg_color=pal.get("device", "#C8CDD2"))
            self._card.configure(fg_color=pal.get("device", "#C8CDD2"))
            self.calc_btn.configure(
                fg_color=pal.get("orange", "#E67E36"),
                hover_color=pal.get("orange", "#E67E36"),
                text_color=pal.get("accent_text", "#FFFFFF"),
            )
        except Exception:
            pass
