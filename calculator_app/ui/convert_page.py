import tkinter as tk
import customtkinter as ctk
from ..core.units import UnitConverter

class ConvertPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=12)
        self._build()

    # ---- Convert Tab ---------------------------------------------------------
    def _build(self):
        frame = self

        top = ctk.CTkFrame(frame, corner_radius=12)
        top.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(top, text="Category:").pack(side="left", padx=(6, 6))
        self.cat_var = tk.StringVar(value="Length")
        self.cat_menu = ctk.CTkOptionMenu(top, variable=self.cat_var,
                                          values=["Length", "Mass", "Temperature"],
                                          command=lambda _v: self._update_units())
        self.cat_menu.pack(side="left")

        ctk.CTkLabel(top, text="From:").pack(side="left", padx=(12, 6))
        self.from_unit = tk.StringVar()
        self.from_cb = ctk.CTkOptionMenu(top, variable=self.from_unit, values=[])
        self.from_cb.pack(side="left")

        ctk.CTkLabel(top, text="To:").pack(side="left", padx=(12, 6))
        self.to_unit = tk.StringVar()
        self.to_cb = ctk.CTkOptionMenu(top, variable=self.to_unit, values=[])
        self.to_cb.pack(side="left")

        ctk.CTkButton(top, text="Swap", width=80, command=self._swap_units).pack(side="left", padx=8)

        mid = ctk.CTkFrame(frame, corner_radius=12)
        mid.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(mid, text="Value:").pack(side="left", padx=(6, 6))
        self.conv_value = tk.StringVar()
        self.val_entry = ctk.CTkEntry(mid, textvariable=self.conv_value, width=160)
        self.val_entry.pack(side="left", padx=(0, 6))
        self.val_entry.bind("<Return>", lambda e: self.do_convert())

        self.conv_btn = ctk.CTkButton(mid, text="Convert", command=self.do_convert)
        self.conv_btn.pack(side="left", padx=6)

        self.conv_result = tk.StringVar(value="Result: ")
        ctk.CTkLabel(frame, textvariable=self.conv_result, font=("Consolas", 14)).pack(anchor="w", padx=12, pady=(0, 10))

        self._update_units()

    def _update_units(self):
        cat = self.cat_var.get()
        if cat == "Length":
            units = list(UnitConverter.LENGTH_FACTORS.keys())
        elif cat == "Mass":
            units = list(UnitConverter.MASS_FACTORS.keys())
        else:
            units = UnitConverter.TEMP_UNITS
        self.from_cb.configure(values=units)
        self.to_cb.configure(values=units)
        if units:
            self.from_unit.set(units[0])
            self.to_unit.set(units[-1])

    def _swap_units(self):
        fu, tu = self.from_unit.get(), self.to_unit.get()
        self.from_unit.set(tu)
        self.to_unit.set(fu)

    def do_convert(self):
        try:
            value = float(self.conv_value.get())
        except Exception:
            self.conv_result.set("Result: Invalid value")
            return
        fu, tu = self.from_unit.get(), self.to_unit.get()
        try:
            cat = self.cat_var.get()
            if cat == "Length":
                out = UnitConverter.convert_length(value, fu, tu)
            elif cat == "Mass":
                out = UnitConverter.convert_mass(value, fu, tu)
            else:
                out = UnitConverter.convert_temp(value, fu, tu)
            self.conv_result.set(f"Result: {out}")
        except Exception as e:
            self.conv_result.set(f"Error: {e}")

    def apply_theme(self, pal, name):
        pass
