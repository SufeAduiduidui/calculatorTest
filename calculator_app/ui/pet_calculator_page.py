import time
import tkinter as tk
from typing import Dict, Tuple
import customtkinter as ctk
import math
import random

from .pet_widget import PetWidget
from .dialogs import show_cat_bubble

from .sound_player import play as play_sound, play_music, stop_music

class PetCaloriePage(ctk.CTkFrame):
    _CAT_DER_RANGE: dict[str, tuple[float, float]]

    def __init__(self, master, palette=None, theme_name="iOS Light"):
        super().__init__(master, corner_radius=12)
        self._palette = palette or {}
        self._theme_name = theme_name
        self._bgm_path = "assets/JiMi_Canon_in_Dmajor.mp3"

        self._CAT_DER_RANGE = {
            "发育期": (2.0, 2.5),
            "未结扎": (1.4, 1.6),
            "已结扎": (1.2, 1.4),
            "过胖": (0.8, 1.0),
            "过瘦": (1.2, 1.8),
            "11岁以上高龄": (1.1, 1.6),
        }


       self._BRANDS = {
            "猫粮": {
                "Orijen Cat&Kitten": 404.0,
                "Royal Canin Indoor27": 360.0,
                "Purina Pro Plan": 390.0,
                "Firstmate菲斯美 室内猫": 330.0,
                "麻利无谷 老年猫": 339.0,
                "欧恩焙鸭": 353.0,
                "Firstmate菲斯美 鸡": 353.0,
                "安娜玛特(黄袋、有谷)": 354.0,
                "美士鸡 室内猫": 357.0,
                "麻利黑金猎鸟": 358.8,
                "blackwood珀萃 鸡肉火鸡": 360.8,
                "活力枫叶": 360.9,
                "halo健美鸡": 361.0,
                "纽顿无谷鱼T24": 366.0,
                "麻利黑金幼猫": 363.8,
                "荒野盛宴猎食火鸡": 368.9,
                "绿福摩": 369.6,
                "nulo火鸡": 369.6,
                "blackwood珀萃鸡肉鲱鱼": 370.8,
                "罗斯鸡": 371.0,
                "渴望低卡": 371.0,
                "蓝馔无谷鸡肉去毛球": 371.3,
                "tiki烘焙粮鸡肉鸡蛋": 372.2,
                "天衡宝": 373.0,
                "麻利无谷成猫": 373.1,
                "麻利无谷幼猫": 381.0,
                "高窦无骨鸡肉": 375.6,
                "halo敏感肠胃海鲜味": 376.0,
                "美士鸡 老年猫": 376.0,
                "纽顿无谷鸡T22": 377.0,
                "美士鸡 成猫": 378.0,
                "安娜玛特(红袋、无谷)": 378.0,
                "欧恩焙鸡": 379.3,
                "纽翠斯红/鸡肉": 380.0,
                "Halo鸡肉幼猫": 380.0,
                "牛油果鸡肉鲜鱼": 382.0,
                "蓝馔无谷三文鱼成猫": 383.9,
                "希尔斯 泌尿处方": 385.0,
                "梅亚奶奶": 385.0,
                "纽翠斯鱼": 385.5,
                "金素": 386.0,
                "Now成猫无谷鸡肉": 386.2,
                "nulo鸡肉": 386.8,
                "Openfarm 火鸡": 388.0,
                "wellnesscore 火鸡": 390.2,
                "美士鸡幼猫": 392.0,
                "Now幼猫": 394.7,
                "蓝馔无骨鸡幼猫": 395.0,
                "蓝爵幼": 395.4,
                "纽翠斯金汐五种肉": 395.5,
                "曙光鸡": 396.0,
                "Wellness core 原味": 397.7,
                "爱肯拿鱼": 408.0,
                "爱肯拿鸡": 410.0,
                "NG鸡": 410.0,
                "渴望鱼": 412.0,
                "渴望红肉": 412.0,
                "百利无谷鸡": 415.0,
                "渴望鸡": 416.0,
                "尊达鸡肉鱼三文鱼幼猫": 416.2,
                "法米娜 猪、鸭": 419.7,
                "法米娜 鸡、魚": 420.4,
                "Go九种肉": 429.8,
                "百利无谷鸭": 439.7,
                "加卉鸡": 440.0,
                "草本魔力 鱼肉": 441.8,
                "Ga三种鱼": 444.4,
                "百利高蛋白": 447.0,
                "德金 鹿肉": 447.4,
                "草本魔力 鸡肉": 448.0,
                "塞伦盖蒂 牛羊无谷": 457.7,
                "尊达火鸡成猫": 457.7,
                "Ga鸡肉": 460.4,
            },
            "罐头": {
                "希宝金标(85g)": 85.0,
                "天衡宝(156g)": 110.0,
            },
            "冻干": {
                "ZIWI Peak": 520.0,
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
        self._desk_pet = None
        self._desk_pet_bubble = None
        self._desk_pet_click_count = 0
        self._desk_pet_last_click = 0.0
        self._angry_mode = False
        self._angry_modal = None
        self._warning_modal = None
        self._angry_state = 0

        self._build()
        self.apply_theme(self._palette, self._theme_name)

#UI--
    def _build(self):
        root = self

        self.device = ctk.CTkFrame(root, corner_radius=24)
        self.device.pack(fill="both", expand=True, padx=40, pady=20)

        top = ctk.CTkFrame(self.device, fg_color="transparent")
        top.pack(side="top", fill="x", padx=20, pady=(16, 8))
        left = ctk.CTkFrame(top, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True)
        self._title_label = ctk.CTkLabel(left, text="猫咪热量计算器", font=("SF Pro Display", 20, "bold"))
        self._title_label.pack(anchor="w")

        right = ctk.CTkFrame(top, fg_color="transparent")
        right.pack(side="right")
        self._desk_pet = PetWidget(
            right,
            image_path="assets/maodie_changtai.jpg",
            size=(72, 72),
            on_click=self._on_desk_pet_click,
        )
        self._desk_pet.pack(padx=6)
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
        w_row = ctk.CTkFrame(w_block, fg_color="transparent")
        w_row.pack(fill="x", padx=12, pady=(0, 12))
        w_entry = ctk.CTkEntry(w_row, placeholder_text="例如 4.2", textvariable=self.weight_var)
        w_entry.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(w_row, text="kg").pack(side="right", padx=(8, 0))

        
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

    def on_show(self):
        try:
            stop_music(300)#切回页面时保证没有残留的bgm
        except Exception:
            pass

        if self._angry_modal and self._angry_modal.winfo_exists():
            self._angry_modal.focus_force()
            return
        if self._warning_modal and self._warning_modal.winfo_exists():
            try:
                self._warning_modal.grab_release()
            except Exception:
                pass
            self._warning_modal.destroy()
        self._warning_modal = None
        if self._desk_pet_bubble and self._desk_pet_bubble.winfo_exists():
            try:
                self._desk_pet_bubble.destroy()
            except Exception:
                pass
        self._desk_pet_bubble = None
        self._desk_pet_click_count = 0
        self._desk_pet_last_click = 0.0
        self._angry_mode = False
        self._angry_state = 0
        if self._desk_pet and self._desk_pet.winfo_exists():
            self._desk_pet.set_enabled(True)
            self._desk_pet.set_image("assets/maodie_changtai.jpg", size=(72, 72))
            self._desk_pet_bubble = show_cat_bubble(
                self._desk_pet._label,
                "人，你要来喂耄了吗？",
                palette=self._palette,
                direction="left",
                wrap_width=260,
            )

    def _on_desk_pet_click(self):
        if self._angry_mode:
            return
        now = time.time()
        if now - self._desk_pet_last_click > 0.9:
            self._desk_pet_click_count = 0
        self._desk_pet_last_click = now
        self._desk_pet_click_count += 1

        if self._desk_pet_bubble and self._desk_pet_bubble.winfo_exists():
            try:
                self._desk_pet_bubble.destroy()
            except Exception:
                pass
            self._desk_pet_bubble = None

        if self._desk_pet_click_count >= 3:
            self._desk_pet_click_count = 0
            if self._angry_state == 0:
                self._show_warning_modal()
            else:
                self._trigger_angry_pet()
            return

        lines = [
            "人，我是听话的小猫",
            "人，你要记得按时喂猫哦",
            "人，你今天过得怎么样？",
        ]
        if self._desk_pet and self._desk_pet.winfo_exists():
            self._desk_pet_bubble = show_cat_bubble(
                self._desk_pet._label,
                random.choice(lines),
                palette=self._palette,
                direction="left",
                wrap_width=260,
            )

    def _show_warning_modal(self):
        if self._warning_modal and self._warning_modal.winfo_exists():
            self._warning_modal.focus_force()
            return
        pal = self._palette or {}
        hover_soft = pal.get("func_hover", pal.get("surface", "#E5E5EA"))
        border_color = pal.get("border", "#D1D1D6")
        modal = ctk.CTkToplevel(self)
        modal.title("哈！")
        modal.resizable(False, False)
        modal.configure(fg_color=pal.get("surface", "#FFFFFF"))
        modal.transient(self.winfo_toplevel())
        modal.grab_set()
        modal.protocol("WM_DELETE_WINDOW", lambda: None)

        container = ctk.CTkFrame(modal, fg_color=pal.get("surface", "#FFFFFF"), corner_radius=20)
        container.pack(fill="both", expand=True, padx=36, pady=28)

        title_lbl = ctk.CTkLabel(
            container,
            text="哈！",
            font=("SF Pro Display", 24, "bold"),
            text_color=pal.get("text", "#000000"),
        )
        title_lbl.pack(anchor="w")

        content_lbl = ctk.CTkLabel(
            container,
            text="小猫好像不太能接受你的热情？",
            font=("Microsoft YaHei UI", 14),
            text_color=pal.get("subtext", "#6C6C70"),
            justify="left",
            wraplength=360,
        )
        content_lbl.pack(anchor="w", pady=(14, 24))

        btn_row = ctk.CTkFrame(container, fg_color="transparent")
        btn_row.pack(fill="x", pady=(0, 8))

        def close_warning():
            if self._warning_modal and self._warning_modal.winfo_exists():
                try:
                    self._warning_modal.grab_release()
                except Exception:
                    pass
                self._warning_modal.destroy()
            self._warning_modal = None

        def handle_soft():
            close_warning()
            self._angry_state = max(self._angry_state, 1)

        def handle_brave():
            close_warning()
            self._angry_state = max(self._angry_state, 1)
            self._trigger_angry_pet()

        btn_soft = ctk.CTkButton(
            btn_row,
            text="好吧，我会注意适度撸猫",
            command=handle_soft,
            fg_color=pal.get("surface", "#FFFFFF"),
            hover_color=hover_soft,
            text_color=pal.get("text", "#000000"),
            border_width=1,
            border_color=border_color,
            corner_radius=16,
            width=360,
        )
        btn_soft.pack(fill="x", pady=(0, 10))

        btn_brave = ctk.CTkButton(
            btn_row,
            text="明知山有虎，偏向虎山行！",
            command=handle_brave,
            fg_color=pal.get("orange", "#E67E36"),
            hover_color=pal.get("orange", "#E67E36"),
            text_color=pal.get("accent_text", "#FFFFFF"),
            corner_radius=16,
            width=360,
        )
        btn_brave.pack(fill="x")

        modal.update_idletasks()
        parent = self.winfo_toplevel()
        try:
            px = parent.winfo_rootx()
            py = parent.winfo_rooty()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
        except Exception:
            px = py = 100
            pw = ph = 400
        mw = max(modal.winfo_width(), 460)
        mh = max(modal.winfo_height(), 240)
        x = px + (pw - mw) // 2
        y = py + (ph - mh) // 2
        modal.geometry(f"{mw}x{mh}+{int(x)}+{int(y)}")
        btn_soft.focus_set()
        self._warning_modal = modal
        self._angry_state = max(self._angry_state, 1)

    def _trigger_angry_pet(self):
        if self._angry_mode:
            return
        if self._warning_modal and self._warning_modal.winfo_exists():
            try:
                self._warning_modal.grab_release()
            except Exception:
                pass
            self._warning_modal.destroy()
        self._warning_modal = None
        self._angry_state = 2
        self._angry_mode = True
        if self._desk_pet and self._desk_pet.winfo_exists():
            self._desk_pet.set_enabled(False)
            self._desk_pet.set_image("assets/maodie_haqi.gif", size=(72, 72))
        try:
            play_sound("assets/maodie_haqi.mp3")
        except Exception:
            pass

        try:
            self.after(1600, lambda: play_music(self._bgm_path, volume=0.55, loop=True)) #让哈气先出现700ms，再开始循环
        except Exception:
            pass

        self._show_angry_modal()



    def _show_angry_modal(self):
        if self._angry_modal and self._angry_modal.winfo_exists():
            self._angry_modal.focus_force()
            return
        pal = self._palette or {}
        modal = ctk.CTkToplevel(self)
        modal.title("哈！！！")
        modal.resizable(False, False)
        modal.configure(fg_color=pal.get("surface", "#FFFFFF"))
        modal.transient(self.winfo_toplevel())
        modal.grab_set()
        modal.protocol("WM_DELETE_WINDOW", lambda: None)

        container = ctk.CTkFrame(modal, fg_color=pal.get("surface", "#FFFFFF"), corner_radius=20)
        container.pack(fill="both", expand=True, padx=36, pady=30)

        title_lbl = ctk.CTkLabel(
            container,
            text="哈！！！",
            font=("SF Pro Display", 28, "bold"),
            text_color=pal.get("text", "#000000"),
        )
        title_lbl.pack(anchor="w")

        content_lbl = ctk.CTkLabel(
            container,
            text="小猫很生气，并撤回了一个计算器",
            font=("Microsoft YaHei UI", 15),
            text_color=pal.get("subtext", "#6C6C70"),
            justify="left",
            wraplength=380,
        )
        content_lbl.pack(anchor="w", pady=(16, 32))

        exit_btn = ctk.CTkButton(
            container,
            text="耄好，人坏",
            command=self._terminate_application,
            fg_color=pal.get("orange", "#E67E36"),
            hover_color=pal.get("orange", "#E67E36"),
            text_color=pal.get("accent_text", "#FFFFFF"),
            corner_radius=18,
            height=48,
            width=360,
        )
        exit_btn.pack(fill="x")

        modal.update_idletasks()
        parent = self.winfo_toplevel()
        try:
            px = parent.winfo_rootx()
            py = parent.winfo_rooty()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
        except Exception:
            px = py = 100
            pw = ph = 400
        mw = max(modal.winfo_width(), 460)
        mh = max(modal.winfo_height(), 240)
        x = px + (pw - mw) // 2
        y = py + (ph - mh) // 2
        modal.geometry(f"{mw}x{mh}+{int(x)}+{int(y)}")
        exit_btn.focus_set()
        self._angry_modal = modal

    def _terminate_application(self):
        try:
            stop_music(300)
        except Exception:
            pass
        if self._angry_modal and self._angry_modal.winfo_exists():
            try:
                self._angry_modal.grab_release()
            except Exception:
                pass
            self._angry_modal.destroy()
        self._angry_modal = None
        root = self.winfo_toplevel()
        try:
            root.destroy()
        except Exception:
            pass




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


