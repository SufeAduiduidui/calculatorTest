import time
import tkinter as tk
from typing import Dict, Tuple, Optional
import customtkinter as ctk
import math
import random

from .pet_widget import PetWidget
from .dialogs import show_cat_bubble

from .sound_player import play as play_sound, play_music, stop_music

from PIL import Image, ImageSequence



class PetCaloriePage(ctk.CTkFrame):
    _CAT_DER_RANGE: dict[str, tuple[float, float]]

    def __init__(self, master, palette=None, theme_name="iOS Light"):
        super().__init__(master, corner_radius=12)
        self._palette = palette or {}
        self._theme_name = theme_name
        self._bgm_path = "assets/JiMi_Canon_in_Dmajor.mp3"

        self._angry_overlay_gif_path = "assets/maodie_haqi.gif"#愤怒弹窗放大gif
        self._angry_zoom_running = False
        self._angry_zoom_label = None
        self._angry_zoom_ctkimage = None
        self._angry_gif_frames = None
        self._angry_gif_durations = None
        self._angry_gif_start_time = 0.0
        self._angry_zoom_start_size = (0, 0)
        self._angry_zoom_target_size = (0, 0)
        self._angry_zoom_anim_steps = 36
        self._angry_zoom_anim_index = 0
        self._angry_zoom_hold_ms = 5000 #gif放大到位后，继续循环播放ms
        self._angry_zoom_hold_scheduled = False

        self._angry_overlay_win = None#gif使用的全局遮罩层窗口
        self._angry_zoom_parent = None#遮罩层

        self._howto_stage_path = "assets/howtojudge.jpeg"#怎么判断猫儿体格图片

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
                "Firstmate菲斯美": {
                    "室内猫": 330.0,
                    "鸡": 353.0,
                },
                "麻利": {
                    "无谷老年猫": 339.0,
                    "黑金猎鸟": 358.8,
                    "黑金幼猫": 363.8,
                    "无谷成猫": 373.1,
                    "无谷幼猫(3755)": 375.5,
                    "无谷幼猫(3810)": 381.0,
                },
                "欧恩焙": {
                    "鸭": 353.0,
                    "鸡": 379.3,
                },
                "安娜玛特": {
                    "(黄袋、有谷)": 354.0,
                    "(红袋、无谷)": 378.0,
                },
                "美士": {
                    "鸡室内猫": 357.0,
                    "鸡老年猫": 376.0,
                    "鸡成猫": 378.0,
                    "鸡幼猫": 392.0,
                },
                "blackwood": {
                    "珀萃 鸡肉火鸡": 360.8,
                    "珀萃 鸡肉鲱鱼": 370.8,
                },
                "活力枫叶": {
                    "未标注": 360.9,
                },
                "Halo": {
                    "健美鸡": 361.0,
                    "敏感肠胃海鲜味": 376.0,
                    "鸡肉幼猫": 380.0,
                },
                "纽顿": {
                    "无谷鱼T24": 366.0,
                    "无谷鸡T22": 377.0,
                },
                "荒野盛宴": {
                    "猎食火鸡": 368.9,
                },
                "绿福摩": {
                    "未标注": 369.6,
                },
                "Nulo": {
                    "火鸡": 369.6,
                    "鸡肉": 386.8,
                },
                "罗斯": {
                    "鸡": 371.0,
                },
                "渴望": {
                    "低卡": 371.0,
                    "鱼": 412.0,
                    "红肉": 412.0,
                    "鸡": 416.0,
                },
                "蓝馔": {
                    "无谷鸡肉去毛球": 371.3,
                    "无谷三文鱼成猫": 383.9,
                    "无骨鸡幼猫": 395.0,
                },
                "Tiki": {
                    "烘焙粮鸡肉鸡蛋": 372.2,
                },
                "天衡宝": {
                    "未标注": 373.0,
                },
                "高窦": {
                    "无骨鸡肉": 375.6,
                },
                "牛油果": {
                    "鸡肉鲜鱼": 382.0,
                },
                "希尔斯": {
                    "泌尿处方": 385.0,
                },
                "梅亚奶奶": {
                    "未标注": 385.0,
                },
                "纽翠斯": {
                    "红/鸡肉": 380.0,
                    "鱼": 385.5,
                    "金汐五种肉": 395.5,
                },
                "金素": {
                    "未标注": 386.0,
                },
                "Now": {
                    "成猫无谷鸡肉": 386.2,
                    "幼猫": 394.7,
                },
                "Open Farm": {
                    "火鸡": 388.0,
                },
                "Wellness Core": {
                    "火鸡": 390.2,
                    "原味": 397.7,
                },
                "蓝爵": {
                    "幼": 395.4,
                },
                "曙光": {
                    "鸡": 396.0,
                },
                "爱肯拿": {
                    "鱼": 408.0,
                    "鸡": 410.0,
                },
                "NG": {
                    "鸡": 410.0,
                },
                "百利": {
                    "无谷鸡": 415.0,
                    "无谷鸭": 439.7,
                    "高蛋白": 447.0,
                },
                "尊达": {
                    "鸡肉鱼三文鱼幼猫": 416.2,
                    "火鸡成猫": 457.7,
                },
                "法米娜": {
                    "猪、鸭": 419.7,
                    "鸡、魚": 420.4,
                },
                "Go": {
                    "九种肉": 429.8,
                },
                "加卉": {
                    "鸡": 440.0,
                },
                "草本魔力": {
                    "鱼肉": 441.8,
                    "鸡肉": 448.0,
                },
                "Ga": {
                    "三种鱼": 444.4,
                    "鸡肉": 460.4,
                },
                "德金": {
                    "鹿肉": 447.4,
                },
                "塞伦盖蒂": {
                    "牛羊无谷": 457.7,
                },
            },
            "罐头": {
                "百利": {
                    "鸡肉": 123.9,
                    "鸭肉": 125.0,
                    "三文鱼": 105.7,
                    "兔肉": 94.4,
                    "羊肉": 132.2,
                    "鹿肉马鲛鱼羊肉": 127.8,
                    "鸡肉羊肉": 132.5,
                },

                "Halo": {
                    "沙丁鱼": 109.6,
                    "鳕鱼": 105.0,
                    "鸡肉鹌鹑": 82.9,
                    "牛肉鮭色": 94.5,
                    "小牛肉": 92.6,
                },

                "麻利": {
                    "鸭肉": 112.8,
                },

                "RAWZ": {
                    "鸡肉鸡肝": 85.9,
                    "鸡肉金枪鱼": 82.7,
                    "鸡胸南瓜": 82.7,
                    "金枪鱼鲑鱼": 85.9,
                    "鸡肉": 83.3,
                    "鸡胸鸭肉": 87.2,
                    "鹿肉马鲛鱼羊肉": 120.0,
                    "东海角": 150.0,
                    "羊肉": 121.1,
                    "兔子": 135.8,
                },

                "巅峰": {
                    "马鲛鱼": 107.5,
                    "奥塔哥山谷": 125.0,
                    "鸡": 94.0,
                    "牛肉": 112.3,
                    "鸡肉": 147.4,
                },

                "Venandi": {
                    "养心帝王鲑": 106.0,
                    "牛肉(937)": 93.7,
                    "鸡肉鸭肉": 73.2,
                    "手撕鸡肉": 85.0,
                    "牛肉(1442)": 144.2,
                },

                "TikiCat黑夜传说": {
                    "鸡肉牛肉": 74.1,
                    "鸡肉三文鱼": 90.0,
                    "火鸡鲑鱼": 98.2,
                    "马肉": 96.0,
                    "鸭肉三文鱼": 147.4,
                },

                "莉莉圆盒": {
                    "鸡肉羊肉": 76.6,
                    "鸡肉牛肉": 92.0,
                    "鸭肉南瓜": 93.6,
                    "小牛肉": 99.5,
                    "牛肉": 149.0,
                    "绵羊肉": 95.0,
                },

                "Majmjam": {
                    "鸡肉盛夏": 82.3,
                    "家禽": 86.0,
                    "鸡肉南瓜": 94.6,
                    "火鸡胎贝": 90.7,
                    "鹿鸡": 127.0,
                    "山羊": 127.0,
                    "鸡肉兔肉": 91.0,
                },

                "卡宠": {
                    "猪鸡": 92.0,
                    "火鸡胡萝卜": 94.0,
                    "负鼠鸡": 124.0,
                    "鸭": 154.0,
                },

                "Ocanis": {
                    "羊三文鱼": 159.0,
                    "鸡三文鱼": 132.0,
                    "火鸡鹌鹑": 91.0,
                },
            },
            "冻干": {
                "sc": {
                    "火鸡": 491.0,
                    "兔": 463.0,
                },
                "K9": {
                    "牛鱼": 476.2,
                    "鸭": 490.5,
                },
                "PR": {
                    "火鸡": 433.8,
                    "牛鱼": 486.7,
                },
                "VE": {
                    "鸡饼/粒": 410.5,
                    "牛肉鸡饼/粒": 497.0,
                    "鸡": 380.7,
                },
                "大西北": {
                    "兔": 387.5,
                },
                "Steve's": {
                    "火鸡&鸭": 493.0,
                    "兔": 352.7,
                },
                "purpose": {
                    "火鸡": 388.0,
                },
                "Meow": {
                    "鸡肉三文鱼": 514.9,
                    "负鼠": 419.9,
                },
                "Nulo": {
                    "鸡鱼": 443.7,
                },
            },

            "混合": {}
        }

        #变量
        self.weight_var = tk.StringVar(value="")
        self.stage_var = tk.StringVar(value="已结扎")
        self.der_var = tk.StringVar(value="")
        self.food_var = tk.StringVar(value="猫粮")
        self.brand_var = tk.StringVar(value="自定义")
        self.kcal_var = tk.StringVar(value="380")  # 默认猫粮
        self.result_var = tk.StringVar(value="每日建议：- g（- kcal）")
        self.rer_text = tk.StringVar(value="RER：- kcal/日")
        self.der_text = tk.StringVar(value="DER：- kcal/日")


        self._der_range = self._CAT_DER_RANGE[self.stage_var.get()]
        self._desk_pet = None
        self._desk_pet_bubble = None
        self._desk_pet_click_count = 0
        self._desk_pet_last_click = 0.0
        self._angry_mode = False
        self._angry_modal = None
        self._warning_modal = None
        self._angry_state = 0

        self._mix_rows = [] #混合编辑器的3行控件与变量
        self.mix_details_var = tk.StringVar(value="")

        self._layout_breakpoint = 920 #宽度小于此值时采用单列布局

        self.brand_primary_var = tk.StringVar(value="自定义")
        self.brand_product_var = tk.StringVar(value="自定义")

        self._catalog = self._build_catalog() #根据 _BRANDS构建嵌套目录：{分类: {品牌: {产品: kcal/100g}}}
        self._started = False #是否点击开始计算

        self._calc_ok = False #_update_preview是否成功产出

        self._build()
        self.apply_theme(self._palette, self._theme_name)

    # UI--
    def _build(self):
        root = self

        self.device = ctk.CTkFrame(root, corner_radius=24)
        self.device.pack(fill="both", expand=True, padx=40, pady=20)

        top = ctk.CTkFrame(self.device, fg_color="透明") if False else ctk.CTkFrame(self.device, fg_color="transparent")
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

        card = ctk.CTkScrollableFrame(self.device, corner_radius=20) #仅类型变为可滚动
        card.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self._card = card

        self._grid_panel = ctk.CTkFrame(card, fg_color="transparent")#网格面板
        self._grid_panel.pack(fill="both", expand=True)

        self._grid_panel.grid_columnconfigure(0, weight=1, uniform="cols")#替换/补充列配置，设置 uniform 保证两列等宽
        self._grid_panel.grid_columnconfigure(1, weight=1, uniform="cols")

        self._slot_top = ctk.CTkFrame(self._grid_panel, fg_color="transparent")
        self._slot_left1 = ctk.CTkFrame(self._grid_panel, fg_color="transparent")
        self._slot_right1 = ctk.CTkFrame(self._grid_panel, fg_color="transparent")
        self._slot_left2 = ctk.CTkTFrame(self._grid_panel, fg_color="transparent") if False else ctk.CTkFrame(self._grid_panel, fg_color="transparent")
        self._slot_right2 = ctk.CTkFrame(self._grid_panel, fg_color="transparent")

        self._slot_row3 = ctk.CTkFrame(self._grid_panel, fg_color="transparent")#把原先左右位改为单一槽位，始终占满两列

        self._slot_bottom = ctk.CTkFrame(self._grid_panel, fg_color="transparent")

        # 初始网格位置（将由 _reflow_layout 调整）
        self._slot_top.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=16, pady=(16, 8))
        self._slot_left1.grid(row=1, column=0, sticky="nsew", padx=(16, 8), pady=8)
        self._slot_right1.grid(row=1, column=1, sticky="nsew", padx=(8, 16), pady=8)
        self._slot_left2.grid(row=2, column=0, sticky="nsew", padx=(16, 8), pady=8)
        self._slot_right2.grid(row=2, column=1, sticky="nsew", padx=(8, 16), pady=8)

        self._slot_row3.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=16, pady=8)

        self._slot_bottom.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=16, pady=(8, 16))

        res_row = ctk.CTkFrame(self._slot_top, fg_color="transparent")  # 结果显示
        res_row.pack(fill="x", padx=0, pady=(0, 6))
        res = ctk.CTkEntry(res_row, textvariable=self.result_var, justify="right", state="disabled")
        res.pack(fill="x")

        info_row = ctk.CTkFrame(self._slot_top, fg_color="transparent")
        info_row.pack(fill="x", padx=0, pady=(0, 2))
        ctk.CTkLabel(info_row, textvariable=self.rer_text).pack(side="left")
        ctk.CTkLabel(info_row, textvariable=self.der_text).pack(side="right")

        w_block = ctk.CTkFrame(self._slot_left1, corner_radius=14)
        w_block.pack(fill="x")

        ctk.CTkLabel(w_block, text="体重").pack(anchor="w", padx=12, pady=(10, 2))
        w_row = ctk.CTkFrame(w_block, fg_color="transparent")
        w_row.pack(fill="x", padx=12, pady=(0, 12))
        w_entry = ctk.CTkEntry(w_row, placeholder_text="例如 4.2", textvariable=self.weight_var)
        w_entry.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(w_row, text="kg").pack(side="right", padx=(8, 0))

        self.weight_var.trace_add("write", lambda *_: (setattr(self, "_started", False), self._update_preview()))

        s_block = ctk.CTkFrame(self._slot_right1, corner_radius=14)
        s_block.pack(fill="x")
        ctk.CTkLabel(s_block, text="阶段").pack(anchor="w", padx=12, pady=(10, 2))
        s_row = ctk.CTkFrame(s_block, fg_color="transparent")
        s_row.pack(fill="x", padx=12, pady=(0, 12))
        self.stage_menu = ctk.CTkOptionMenu(s_row,
                                            values=list(self._CAT_DER_RANGE.keys()),
                                            command=self._on_stage_change,
                                            variable=self.stage_var)
        self.stage_menu.pack(side="left")

        ctk.CTkButton(
            s_row,
            text="如何判断您家猫儿是什么状态",
            command=self._open_stage_help,
            width=220
        ).pack(side="right", padx=(8, 0))

        self.stage_tip = ctk.CTkLabel(s_row, text="")
        self.stage_tip.pack(side="right")

        der_block = ctk.CTkFrame(self._slot_left2, corner_radius=14)
        der_block.pack(fill="x")
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

        chips_block = ctk.CTkFrame(self._slot_right2, corner_radius=14)  # 食物类
        chips_block.pack(fill="x")
        ctk.CTkLabel(chips_block, text="食物类型").pack(anchor="w", padx=12, pady=(10, 2))
        chips = ctk.CTkFrame(chips_block, fg_color="transparent")
        chips.pack(fill="x", padx=12, pady=(0, 12))
        self._chip_buttons = []
        for label in ["猫粮", "罐头", "冻干", "混合"]:
            btn = ctk.CTkButton(chips, text=label, corner_radius=16, width=80,
                                command=lambda t=label: self._select_food(t))
            btn.pack(side="left", padx=6, pady=6)
            self._chip_buttons.append(btn)

        # 品牌与热量（二级菜单）
        brand_block = ctk.CTkFrame(self._slot_row3, corner_radius=14)
        brand_block.pack(fill="x")
        self._brand_block = brand_block #保存引用，便于显隐

        ctk.CTkLabel(brand_block, text="品牌与热量").pack(anchor="w", padx=12, pady=(10, 2))

        #一级：品牌
        br_row1 = ctk.CTkFrame(brand_block, fg_color="透明") if False else ctk.CTkFrame(brand_block, fg_color="transparent")
        br_row1.pack(fill="x", padx=12, pady=(0, 6))
        ctk.CTkLabel(br_row1, text="品牌").pack(side="left")
        self.brand_primary_menu = ctk.CTkOptionMenu(
            br_row1,
            variable=self.brand_primary_var,
            values=["自定义"],
            command=self._on_brand_primary_change,
            width=220
        )
        self.brand_primary_menu.pack(side="left", padx=(6, 0))

        #二级：种类+xx kcal/100g
        br_row2 = ctk.CTkFrame(brand_block, fg_color="透明") if False else ctk.CTkFrame(brand_block, fg_color="transparent")
        br_row2.pack(fill="x", padx=12, pady=(0, 12))
        ctk.CTkLabel(br_row2, text="产品").pack(side="left")
        self.brand_product_menu = ctk.CTkOptionMenu(
            br_row2,
            variable=self.brand_product_var,
            values=["自定义"],
            command=self._on_brand_product_change,
            width=260
        )
        self.brand_product_menu.pack(side="left", padx=(6, 0))

        ctk.CTkLabel(br_row2, text="kcal/100g").pack(side="right")
        self.kcal_entry = ctk.CTkEntry(br_row2, width=120, textvariable=self.kcal_var)
        self.kcal_entry.pack(side="right", padx=(0, 8))

        # 混合编辑器：支持二级菜单（品牌/产品）
        self.mix_block = ctk.CTkFrame(self._slot_row3, corner_radius=14)  # 混合编辑器，仅在选择混合时显示
        self._mix_block = self.mix_block  # 保存引用，便于显隐
        self.mix_block.pack_forget()

        mix_title = ctk.CTkLabel(self.mix_block, text="混合编辑器（选择 2～3 种，比例为克数占比）")
        mix_title.pack(anchor="w", padx=12, pady=(10, 2))

        self._mix_rows = []
        default_cats = ["罐头", "冻干", "猫粮"]
        for i in range(3):
            row = ctk.CTkFrame(self.mix_block, fg_color="透明") if False else ctk.CTkFrame(self.mix_block, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=6)

            cat_var = tk.StringVar(value=default_cats[i % len(default_cats)])
            brand_var = tk.StringVar(value="")
            prod_var = tk.StringVar(value="")
            ratio_var = tk.StringVar(value="")

            ctk.CTkLabel(row, text=f"{i + 1}.").pack(side="left", padx=(0, 6))
            cat_menu = ctk.CTkOptionMenu(
                row, variable=cat_var,
                values=["罐头", "冻干", "猫粮"],
                width=110,
                command=lambda _v, idx=i: self._on_mix_cat_change(idx)
            )
            cat_menu.pack(side="left", padx=(0, 8))

            brand_menu = ctk.CTkOptionMenu(
                row, variable=brand_var,
                values=[""],
                width=180,
                command=lambda _v, idx=i: self._on_mix_brand_change(idx),
            )
            brand_menu.pack(side="left", padx=(0, 8))

            prod_menu = ctk.CTkOptionMenu(
                row, variable=prod_var,
                values=[""],
                width=220,
                command=lambda _v, idx=i: self._on_mix_product_change(idx),
            )
            prod_menu.pack(side="left", padx=(0, 8))

            ctk.CTkLabel(row, text="比例(%)").pack(side="left", padx=(12, 6))
            ratio_entry = ctk.CTkEntry(row, textvariable=ratio_var, width=100)
            ratio_entry.pack(side="left")

            ratio_var.trace_add("write", lambda *_: (setattr(self, "_started", False), self._update_preview()))

            self._mix_rows.append(
                {
                    "frame": row,
                    "cat_var": cat_var,
                    "brand_var": brand_var,
                    "prod_var": prod_var,
                    "ratio_var": ratio_var,
                    "cat_menu": cat_menu,
                    "brand_menu": brand_menu,
                    "prod_menu": prod_menu,
                    "ratio_entry": ratio_entry,
                }
            )
            self._refresh_mix_brand_values(i)
            self._refresh_mix_product_values(i)

        mix_btns = ctk.CTkFrame(self.mix_block, fg_color="透明") if False else ctk.CTkFrame(self.mix_block, fg_color="transparent")
        mix_btns.pack(fill="x", padx=12, pady=(0, 8))
        ctk.CTkButton(mix_btns, text="均分", width=80, command=self._mix_equalize).pack(side="left", padx=(0, 6))
        ctk.CTkButton(mix_btns, text="清空", width=80, command=self._mix_clear).pack(side="left", padx=(0, 6))

        ctk.CTkLabel(self.mix_block, text="混合明细：").pack(anchor="w", padx=12, pady=(0, 2))
        mix_details = ctk.CTkLabel(self.mix_block, textvariable=self.mix_details_var, justify="left")
        mix_details.pack(anchor="w", padx=12, pady=(0, 12))

        # 底部操作：开始计算
        bottom = ctk.CTkFrame(self._slot_bottom, fg_color="透明") if False else ctk.CTkFrame(self._slot_bottom, fg_color="transparent")
        bottom.pack(fill="x", padx=0, pady=(0, 0))
        self._start_btn = ctk.CTkButton(bottom, text="开始计算", height=40, command=self._on_start_press)
        self._start_btn.pack(fill="x", padx=12, pady=(6, 6))

        self._apply_stage_range_text()
        self._reset_der_to_middle()
        self._select_food("猫粮") #初始化选中与配色

        self._grid_panel.bind("<Configure>", lambda e: self._reflow_layout())

    # 目录
    def _build_catalog(self) -> Dict[str, Dict[str, Dict[str, float]]]:
        catalog: Dict[str, Dict[str, Dict[str, float]]] = {}
        for cat, brands in self._BRANDS.items():
            new_brands: Dict[str, Dict[str, float]] = {}
            if isinstance(brands, dict):
                for b, prods in brands.items():
                    if isinstance(prods, dict):
                        new_brands[b] = dict(prods)
            catalog[cat] = new_brands
        return catalog

    # 阶段/DER
    def _on_stage_change(self, _value):
        self._started = False
        self._der_range = self._CAT_DER_RANGE[self.stage_var.get()]
        try:
            self.der_slider.configure(from_=self._der_range[0], to=self._der_range[1])
        except Exception:
            pass
        self._apply_stage_range_text()
        try:
            v = float(self.der_var.get())
        except Exception:
            v = None
        if v is None or not (self._der_range[0] <= v <= self._der_range[1]):
            self._reset_der_to_middle()
        else:
            try:
                self.der_slider.set(v)
            except Exception:
                pass
        self._update_preview()

    def _apply_stage_range_text(self):
        lo, hi = self._der_range
        self.der_range_lbl.configure(text=f"范围：{lo:.1f} ～ {hi:.1f}")
        self.stage_tip.configure(text=f"建议 {((lo + hi) / 2):.1f}")

    def _reset_der_to_middle(self):
        mid = (self._der_range[0] + self._der_range[1]) / 2
        self.der_var.set(f"{mid:.2f}")
        try:
            self.der_slider.set(mid)
        except Exception:
            pass

    def _on_der_slider(self, value: float):
        self._started = False
        try:
            self.der_var.set(f"{float(value):.2f}")
        except Exception:
            pass
        self._update_preview()

    def _on_der_entry_commit(self):
        self._started = False
        try:
            v = float(self.der_var.get())
        except Exception:
            v = (self._der_range[0] + self._der_range[1]) / 2
            self.der_var.set(f"{v:.2f}")
        v = max(self._der_range[0], min(self._der_range[1], v))
        self.der_var.set(f"{v:.2f}")
        try:
            self.der_slider.set(v)
        except Exception:
            pass
        self._update_preview()

    # 食物/品牌/产品（二级菜单）
    def _select_food(self, food: str):
        self._started = False
        self.food_var.set(food)
        self._style_food_chips()  # 橙色选中

        if food == "混合":
            self._brand_block.pack_forget()
            self._mix_block.pack(fill="x")
        else:
            self._mix_block.pack_forget()
            self._brand_block.pack(fill="x")
            self._refresh_brand_menus_for(food)

        self._update_preview()

    def _style_food_chips(self):
        pal = self._palette or {}
        sel = self.food_var.get()
        for b in self._chip_buttons:
            label = b.cget("text")
            if label == sel:
                b.configure(
                    fg_color=pal.get("orange", "#E67E36"),
                    hover_color=pal.get("orange", "#E67E36"),
                    text_color=pal.get("accent_text", "#FFFFFF"),
                    border_width=0,
                )
            else:
                b.configure(
                    fg_color=pal.get("func", "#9AA1A8"),
                    hover_color=pal.get("func_hover", "#8F969E"),
                    text_color=pal.get("text", "#000000"),
                    border_width=1,
                    border_color=pal.get("func_border", "#8A9299"),
                )

    def _refresh_brand_menus_for(self, food: str):
        brands = sorted(list(self._catalog.get(food, {}).keys()))
        values = ["自定义"] + brands if brands else ["自定义"]
        if self.brand_primary_var.get() not in values:
            self.brand_primary_var.set("自定义")
        self.brand_primary_menu.configure(values=values)
        self._on_brand_primary_change(self.brand_primary_var.get())

    def _on_brand_primary_change(self, value: str):
        self._started = False
        food = self.food_var.get()
        if value == "自定义":
            self.brand_product_menu.configure(values=["自定义"])
            self.brand_product_var.set("自定义")
            self.kcal_entry.configure(state="normal")
        else:
            prods = sorted(list(self._catalog.get(food, {}).get(value, {}).keys()))
            values = ["自定义"] + prods if prods else ["自定义"]
            self.brand_product_menu.configure(values=values)
            if prods:
                first = prods[0]
                self.brand_product_var.set(first)
                kcal = self._catalog[food][value][first]
                self.kcal_var.set(f"{kcal:.1f}")
                self.kcal_entry.configure(state="disabled")
            else:
                self.brand_product_var.set("自定义")
                self.kcal_entry.configure(state="normal")
        self._update_preview()

    def _on_brand_product_change(self, value: str):
        self._started = False
        food = self.food_var.get()
        brand = self.brand_primary_var.get()
        if value == "自定义" or brand == "自定义":
            self.kcal_entry.configure(state="normal")
        else:
            kcal = self._catalog.get(food, {}).get(brand, {}).get(value, None)
            if isinstance(kcal, (int, float)):
                self.kcal_var.set(f"{kcal:.1f}")
                self.kcal_entry.configure(state="disabled")
            else:
                self.kcal_entry.configure(state="normal")
        self._update_preview()

    # 混合编辑器
    def _refresh_mix_brand_values(self, idx: int):
        row = self._mix_rows[idx]
        cat = row["cat_var"].get()
        brands = sorted(list(self._catalog.get(cat, {}).keys()))
        values = [""] + brands
        row["brand_menu"].configure(values=values)
        if row["brand_var"].get() not in values:
            row["brand_var"].set("")

    def _refresh_mix_product_values(self, idx: int):
        row = self._mix_rows[idx]
        cat = row["cat_var"].get()
        brand = row["brand_var"].get()
        if brand and brand in self._catalog.get(cat, {}):
            prods = sorted(list(self._catalog[cat][brand].keys()))
            values = [""] + prods
        else:
            values = [""]
        row["prod_menu"].configure(values=values)
        if row["prod_var"].get() not in values:
            row["prod_var"].set("")

    def _on_mix_cat_change(self, idx: int):
        self._started = False
        self._refresh_mix_brand_values(idx)
        self._refresh_mix_product_values(idx)
        self._update_preview()

    def _on_mix_brand_change(self, idx: int):
        self._started = False
        self._refresh_mix_product_values(idx)
        self._update_preview()

    def _on_mix_product_change(self, idx: int):
        self._started = False
        self._update_preview()

    def _mix_equalize(self):
        self._started = False
        rows = []
        for row in self._mix_rows:
            cat = row["cat_var"].get().strip()
            brand = row["brand_var"].get().strip()
            prod = row["prod_var"].get().strip()
            if cat and brand and prod:
                rows.append(row)
        if not rows:
            return
        percentage = 100.0 / len(rows)  # 均分百分比
        for r in rows:
            r["ratio_var"].set(f"{percentage:.1f}")
        self._update_preview()

    def _mix_clear(self):
        self._started = False
        for row in self._mix_rows:
            row["brand_var"].set("")
            row["prod_var"].set("")
            row["ratio_var"].set("")
            self._refresh_mix_brand_values(self._mix_rows.index(row))
            self._refresh_mix_product_values(self._mix_rows.index(row))
        self.mix_details_var.set("")
        self._update_preview()

    # 计算
    def _parse_weight(self) -> Optional[float]:
        s = self.weight_var.get().strip()
        try:
            w = float(s)
            if w > 0:
                return w
        except Exception:
            pass
        return None

    def _calc_rer_der(self) -> tuple[Optional[float], Optional[float], Optional[float]]:
        w = self._parse_weight()
        if not w:
            self.rer_text.set("RER：- kcal/日")
            self.der_text.set("DER：- kcal/日")
            return None, None, None
        rer = 70.0 * (w ** 0.75)
        try:
            coeff = float(self.der_var.get())
        except Exception:
            coeff = (self._der_range[0] + self._der_range[1]) / 2
            self.der_var.set(f"{coeff:.2f}")
        der = rer * coeff
        self.rer_text.set(f"RER：{rer:.1f} kcal/日")
        self.der_text.set(f"DER：{der:.1f} kcal/日（系数 x{coeff:.2f}）")
        return w, rer, der

    def _get_single_kcal_per_100g(self) -> Optional[float]:
        food = self.food_var.get()
        if food == "混合":
            return None
        brand = self.brand_primary_var.get()
        prod = self.brand_product_var.get()
        if brand != "自定义" and prod != "自定义":
            kcal = self._catalog.get(food, {}).get(brand, {}).get(prod, None)
            if isinstance(kcal, (int, float)):
                return float(kcal)
        try:
            kcal = float(self.kcal_var.get())
            if kcal > 0:
                return kcal
        except Exception:
            pass
        return None

    def _get_mix_kcal_per_100g(self) -> tuple[Optional[float], str]:
        items = []
        detail_lines = []
        total_ratio = 0.0
        for i, row in enumerate(self._mix_rows, start=1):
            cat = row["cat_var"].get().strip()
            brand = row["brand_var"].get().strip()
            prod = row["prod_var"].get().strip()
            ratio_s = row["ratio_var"].get().strip()
            if not ratio_s:
                continue
            try:
                ratio = float(ratio_s)
                if ratio <= 0:
                    continue
            except Exception:
                continue
            kcal = None
            if cat in self._catalog and brand in self._catalog[cat] and prod in self._catalog[cat][brand]:
                kcal = float(self._catalog[cat][brand][prod])
            if kcal is None:
                continue
            items.append((ratio, kcal, cat, brand, prod))
            total_ratio += ratio

        if not items or len(items) < 2:
            if getattr(self, "_started", False):
                try:
                    play_sound("assets/xp_wrong.mp3")
                except Exception:
                    pass
            return None, "提示：请至少选择两种以上且填写比例（%）"

        if abs(total_ratio - 100.0) > 1:#检查比例加和是否为100%，允许少量误差
            if getattr(self, "_started", False):
                try:
                    play_sound("assets/xp_wrong.mp3")
                    return None, "加和要=100%"
                except Exception:
                    pass

        weighted = sum(r * k for (r, k, _, _, _) in items) / total_ratio
        for ratio, kcal, cat, brand, prod in items:
            detail_lines.append(f"- {cat} / {brand} / {prod}：{kcal:.1f} kcal/100g，比例 {ratio:g}%")
        detail_text = "\n".join(detail_lines) + f"\n混合后：{weighted:.1f} kcal/100g"
        return weighted, detail_text

    def _update_preview(self):
        self._calc_ok = False
        _, _, der = self._calc_rer_der()
        if der is None:
            self.result_var.set("每日建议：- g（- kcal）")
            self.mix_details_var.set("")
            return

        # 未点击“开始计算”时，不展示结果与明细
        if not self._started:
            self.result_var.set("每日建议：- g（- kcal）")
            self.mix_details_var.set("")
            return

        food = self.food_var.get()
        kcal_100g = None
        mix_detail = ""

        if food == "混合":
            kcal_100g, mix_detail = self._get_mix_kcal_per_100g()
            self.mix_details_var.set(mix_detail or "")
        else:
            kcal_100g = self._get_single_kcal_per_100g()
            self.mix_details_var.set("")

        if not kcal_100g or kcal_100g <= 0:
            self.result_var.set("每日建议：- g（- kcal）")
            return

        grams = der * 100.0 / kcal_100g
        self.result_var.set(f"每日建议：{grams:.0f} g（{der:.0f} kcal）")
        self._calc_ok = True

    def _on_start_press(self):
        if self._parse_weight() is None:#先校验体重；缺失则在结果区提示并保持未开始
            self._started = False
            self.result_var.set("请输入你的猫儿或狗儿的体重～")
            try:
                play_sound("assets/xp_wrong.mp3") #错误提示音
            except Exception:
                pass
            return

        self._started = True
        self._update_preview()
        if self._calc_ok:  # 仅成功时播放
            try:
                play_sound("assets/cat.mp3")
            except Exception:
                pass


    # 布局
    def _reflow_layout(self):
        try:
            width = self._grid_panel.winfo_width()
        except Exception:
            return
        single = width < self._layout_breakpoint
        try:
            self._slot_top.grid_configure(row=0, column=0, columnspan=2, padx=16, pady=(16, 8), sticky="nsew")
            if single:
                self._slot_left1.grid_configure(row=1, column=0, columnspan=2, padx=16, pady=8, sticky="nsew")
                self._slot_right1.grid_configure(row=2, column=0, columnspan=2, padx=16, pady=8, sticky="nsew")
                self._slot_left2.grid_configure(row=3, column=0, columnspan=2, padx=16, pady=8, sticky="nsew")
                self._slot_right2.grid_configure(row=4, column=0, columnspan=2, padx=16, pady=8, sticky="nsew")
                self._slot_row3.grid_configure(row=5, column=0, columnspan=2, padx=16, pady=8, sticky="nsew")
                self._slot_bottom.grid_configure(row=6, column=0, columnspan=2, padx=16, pady=(8, 16), sticky="nsew")
            else:
                self._slot_left1.grid_configure(row=1, column=0, columnspan=1, padx=(16, 8), pady=8, sticky="nsew")
                self._slot_right1.grid_configure(row=1, column=1, columnspan=1, padx=(8, 16), pady=8, sticky="nsew")
                self._slot_left2.grid_configure(row=2, column=0, columnspan=1, padx=(16, 8), pady=8, sticky="nsew")
                self._slot_right2.grid_configure(row=2, column=1, columnspan=1, padx=(8, 16), pady=8, sticky="nsew")
                self._slot_row3.grid_configure(row=3, column=0, columnspan=2, padx=16, pady=8, sticky="nsew")
                self._slot_bottom.grid_configure(row=4, column=0, columnspan=2, padx=16, pady=(8, 16), sticky="nsew")
        except Exception:
            pass

    def _on_desk_pet_click(self):  # 耄耋桌宠
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

        tips = [
            "喵~ 记得填体重和选择吃的哦！",
            "再点我几下，看看会发生什么~",
            "今天也要健康吃饭！",
            "人，我是听话的小猫",
            "人，你要记得按时喂猫哦",
            "人，你今天过得怎么样？",
        ]
        self._desk_pet_bubble = show_cat_bubble(
            self._desk_pet._label, random.choice(tips), palette=self._palette, direction="left", wrap_width=260
        )
        try:
            play_sound("assets/cat.mp3")
        except Exception:
            pass

    def _open_stage_help(self):
        pal = self._palette or {}
        path = getattr(self, "_howto_stage_path", "assets/howtojudge.jpeg")

        modal = ctk.CTkToplevel(self)
        modal.title("如何判断猫咪状态")
        modal.resizable(True, True)
        modal.configure(fg_color=pal.get("surface", "#FFFFFF"))
        try:
            modal.transient(self.winfo_toplevel())
            modal.grab_set()
        except Exception:
            pass

        container = ctk.CTkFrame(modal, fg_color=pal.get("surface", "#FFFFFF"), corner_radius=16)
        container.pack(fill="both", expand=True, padx=24, pady=20)

        # 加载图片
        try:
            img = Image.open(path)
        except Exception:
            ctk.CTkLabel(container, text="未找到图片：assets/howtojudge.jpeg").pack(padx=12, pady=12)
            return

        # 计算初始显示尺寸（保持等比，限制最大窗口内）
        modal.update_idletasks()
        max_w, max_h = 820, 980  # 初始最大显示区域，可按需调
        iw, ih = img.size
        scale = min(max_w / iw, max_h / ih, 1.0)
        disp_w, disp_h = max(1, int(iw * scale)), max(1, int(ih * scale))

        # 生成 CTkImage（做一次版本兼容）
        try:
            ctk_img = ctk.CTkImage(img, size=(disp_w, disp_h))
        except TypeError:
            ctk_img = ctk.CTkImage(light_image=img, size=(disp_w, disp_h))

        # 挂到 label 上；保存引用避免被回收
        lbl = ctk.CTkLabel(container, image=ctk_img, text="")
        lbl._ctk_img_ref = ctk_img
        lbl.pack(padx=6, pady=6)

        # 居中窗口
        try:
            parent = self.winfo_toplevel()
            px, py = parent.winfo_rootx(), parent.winfo_rooty()
            pw, ph = parent.winfo_width(), parent.winfo_height()
        except Exception:
            px = py = 100
            pw = ph = 800
        mw = max(disp_w + 48, 420)
        mh = max(disp_h + 96, 320)
        x = px + (pw - mw) // 2
        y = py + (ph - mh) // 2
        modal.geometry(f"{mw}x{mh}+{int(x)}+{int(y)}")

    def on_show(self):
        try:
            stop_music(300)  # 切回页面时保证没有残留的bgm
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

        self.mix_details_var.set("")

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

        try:
            self.after(0, self._reflow_layout)
        except Exception:
            pass

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
            self.after(1600, lambda: play_music(self._bgm_path, volume=0.55, loop=True))  # 让哈气先出现700ms，再开始循环
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

        try:#约4～8秒后启动gif彩蛋
            delay_ms = random.randint(4000, 8000)
            self.after(delay_ms, self._open_overlay_and_start_zoom_gif)
        except Exception:
            pass

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
            ow = getattr(self, "_angry_overlay_win", None)
            if ow and ow.winfo_exists():
                try:
                    ow.destroy()
                except Exception:
                    pass
            self._angry_overlay_win = None
            self._angry_zoom_parent = None

            self._angry_zoom_running = False
            self._angry_zoom_label = None
            self._angry_zoom_ctkimage = None
            self._angry_gif_frames = None
            self._angry_gif_durations = None
        except Exception:
            pass

    def _start_angry_zoom_gif(self, modal):
        self._angry_zoom_hold_scheduled = False
        self._angry_zoom_parent = modal #modal就是遮罩层

        if not modal or not modal.winfo_exists():#对话框已关则退出
            return

        path = getattr(self, "_angry_overlay_gif_path", None) or "assets/maodie_haqi.gif"
        try:
            im = Image.open(path)
        except Exception:
            return
        frames, durations = [], []
        try:
            for frame in ImageSequence.Iterator(im):
                frames.append(frame.convert("RGBA"))
                durations.append(int(frame.info.get("duration", 80)))  # ms
        except Exception:
            frames = [im.convert("RGBA")]
            durations = [100]
        if not frames:
            return

        self._angry_gif_frames = frames
        self._angry_gif_durations = [d if d > 0 else 80 for d in durations]
        self._angry_gif_start_time = time.time()
        self._angry_zoom_anim_index = 0
        self._angry_zoom_anim_steps = 36#放大帧数

        modal.update_idletasks()#计算目标尺寸
        mw, mh = max(1, modal.winfo_width()), max(1, modal.winfo_height())
        start_side = max(60, min(mw, mh) // 6) #从较小正方形开始
        self._angry_zoom_start_size = (start_side, start_side)
        self._angry_zoom_target_size = (mw, mh)

        try:
            self._angry_zoom_ctkimage = ctk.CTkImage(frames[0], size=self._angry_zoom_start_size)
        except TypeError:
            #兼容某些版本需要 light_image=
            self._angry_zoom_ctkimage = ctk.CTkImage(light_image=frames[0], size=self._angry_zoom_start_size)

        if not self._angry_zoom_label or not self._angry_zoom_label.winfo_exists():
            self._angry_zoom_label = ctk.CTkLabel(modal, image=self._angry_zoom_ctkimage, text="",
                                                  fg_color="transparent")
            self._angry_zoom_label.place(relx=0.5, rely=0.5, anchor="center")
        else:
            self._angry_zoom_label.configure(image=self._angry_zoom_ctkimage)
            self._angry_zoom_label.place(relx=0.5, rely=0.5, anchor="center")

        self._angry_zoom_label.lift()
        self._angry_zoom_running = True
        self._animate_angry_zoom_gif()

    def _animate_angry_zoom_gif(self):
        parent = getattr(self, "_angry_zoom_parent", None)
        if not parent or not parent.winfo_exists():
            self._angry_zoom_running = False
            return
        if not getattr(self, "_angry_zoom_running", False):
            return
        if not self._angry_gif_frames:
            self._angry_zoom_running = False
            return
        if not getattr(self, "_angry_zoom_label", None) or not self._angry_zoom_label.winfo_exists():
            self._angry_zoom_running = False
            self._destroy_angry_overlay_win()
            return

        elapsed_ms = int((time.time() - self._angry_gif_start_time) * 1000)
        total_ms = sum(self._angry_gif_durations) or 1000
        t_cycle = elapsed_ms % total_ms
        acc = 0
        frame_idx = 0
        for i, d in enumerate(self._angry_gif_durations):
            acc += d
            if t_cycle < acc:
                frame_idx = i
                break
        frame = self._angry_gif_frames[frame_idx]

        anim_i = self._angry_zoom_anim_index#放大动画，到位后循环播gif
        n = max(1, self._angry_zoom_anim_steps)
        sw, sh = self._angry_zoom_start_size
        tw, th = self._angry_zoom_target_size

        if anim_i < n:
            t = anim_i / n
            t2 = 1 - (1 - t) ** 3
            cur_w = int(sw + (tw - sw) * t2)
            cur_h = int(sh + (th - sh) * t2)
            self._angry_zoom_anim_index += 1
        else:
            cur_w, cur_h = tw, th
            if not self._angry_zoom_hold_scheduled:#5秒后销毁
                self._angry_zoom_hold_scheduled = True
                try:
                    self.after(self._angry_zoom_hold_ms, self._destroy_angry_overlay_win)
                except Exception:
                    pass

        iw, ih = frame.size#等比缩放
        scale = max(cur_w / iw, cur_h / ih)
        disp_w = max(1, int(iw * scale))
        disp_h = max(1, int(ih * scale))

        try:
            self._angry_zoom_ctkimage = ctk.CTkImage(frame, size=(disp_w, disp_h))
        except TypeError:
            self._angry_zoom_ctkimage = ctk.CTkImage(light_image=frame, size=(disp_w, disp_h))
        self._angry_zoom_label.configure(image=self._angry_zoom_ctkimage)
        self._angry_zoom_label.lift()

        remainder = max(1, acc - t_cycle)
        next_ms = max(15, min(40, remainder))
        if self._angry_zoom_running:
            self.after(next_ms, self._animate_angry_zoom_gif)

    def _open_overlay_and_start_zoom_gif(self):
        root = self.winfo_toplevel()
        if not root or not root.winfo_exists():
            return
        try:
            root.update_idletasks()
        except Exception:
            pass

        x, y = root.winfo_rootx(), root.winfo_rooty()
        w, h = max(1, root.winfo_width()), max(1, root.winfo_height())

        win = ctk.CTkToplevel(root)
        try:
            win.overrideredirect(True)
        except Exception:
            pass
        try:
            win.attributes("-topmost", True)#置顶到最上层，盖住对话框
        except Exception:
            pass
        try:
            win.transient(root)
        except Exception:
            pass
        try:
            win.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            pass
        win.configure(fg_color=self._palette.get("surface", "#FFFFFF"))

        self._angry_overlay_win = win
        self._start_angry_zoom_gif(win)

    def _destroy_angry_overlay_win(self):
        win = getattr(self, "_angry_overlay_win", None)
        if win and win.winfo_exists():
            try:
                win.destroy()
            except Exception:
                pass
        self._angry_overlay_win = None
        self._angry_zoom_parent = None

    # 主题
    def apply_theme(self, pal, name):
        self._palette = pal or {}
        self._theme_name = name or self._theme_name

        try:
            self.configure(fg_color=self._palette.get("bg", "#F5F5F5"))
            self.device.configure(fg_color=self._palette.get("device", "#C8CDD2"))
            self._card.configure(fg_color=self._palette.get("device", "#C8CDD2"))
        except Exception:
            pass

        self._title_label.configure(text_color=self._palette.get("text", "#000000"))

        self._style_food_chips()

        try:
            self._start_btn.configure(
                fg_color=self._palette.get("orange", "#E67E36"),
                hover_color=self._palette.get("orange", "#E67E36"),
                text_color=self._palette.get("accent_text", "#FFFFFF"),
                border_width=0,
            )
        except Exception:
            pass










