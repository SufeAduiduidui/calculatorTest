import tkinter as tk
import customtkinter as ctk
import math
from ..core.units import UnitConverter
from ..core.safe_eval import SafeEvaluator

class ConvertPage(ctk.CTkFrame):
    def __init__(self, master, evaluator: SafeEvaluator, palette=None, theme_name="iOS Light"):
        super().__init__(master, corner_radius=12)
        self.evaluator = evaluator
        self._palette = palette
        self._theme_name = theme_name
        self._plot_points = []
        self._plot_bounds = None
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

        ctrl = ctk.CTkFrame(frame, corner_radius=12)
        ctrl.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(ctrl, text="f(x) =").pack(side="left", padx=(6, 6))
        self.func_expr = tk.StringVar(value="sin(x)")
        func_entry = ctk.CTkEntry(ctrl, textvariable=self.func_expr, width=240)
        func_entry.pack(side="left", padx=6)
        func_entry.bind("<Return>", lambda e: self.plot())

        ctk.CTkLabel(ctrl, text="x min").pack(side="left", padx=(12, 4))
        self.xmin_var = tk.StringVar(value="-10")
        ctk.CTkEntry(ctrl, textvariable=self.xmin_var, width=80).pack(side="left", padx=4)

        ctk.CTkLabel(ctrl, text="x max").pack(side="left", padx=(12, 4))
        self.xmax_var = tk.StringVar(value="10")
        ctk.CTkEntry(ctrl, textvariable=self.xmax_var, width=80).pack(side="left", padx=4)

        self.plot_btn = ctk.CTkButton(ctrl, text="Plot", command=self.plot)
        self.plot_btn.pack(side="left", padx=8)

        self.plot_status = tk.StringVar(value="")
        ctk.CTkLabel(frame, textvariable=self.plot_status).pack(anchor="w", padx=10)

        canvas_frame = ctk.CTkFrame(frame, corner_radius=12)
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(canvas_frame, bg="white", highlightthickness=1)
        self.canvas.pack(fill="both", expand=True, padx=6, pady=6)
        self.canvas.bind("<Configure>", lambda e: self._redraw_plot())

        self._update_units()
        self.apply_theme(self._palette, self._theme_name)

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

    def plot(self):
        expr = self.func_expr.get().strip()
        try:
            xmin = float(self.xmin_var.get())
            xmax = float(self.xmax_var.get())
            if xmax <= xmin:
                raise ValueError("x max must be > x min")
        except Exception as e:
            self.plot_status.set(f"Error: {e}")
            return

        samples = max(400, min(1200, int(max(self.canvas.winfo_width(), 1))))
        xs = [xmin + (xmax - xmin) * i / (samples - 1) for i in range(samples)]
        valid_points = []
        err_count = 0

        for x in xs:
            try:
                y = self.evaluator.evaluate(expr, variables={"x": x})
                if isinstance(y, (int, float)) and math.isfinite(y):
                    valid_points.append((x, float(y)))
                else:
                    err_count += 1
            except Exception:
                err_count += 1

        if not valid_points:
            self.plot_status.set("Error: no valid points to plot")
            self._plot_points = []
            self._plot_bounds = None
            if not math.isfinite(ymin) or not math.isfinite(ymax) or ymin == ymax:
                ymin, ymax = ymin - 1.0, ymax + 1.0

        self._plot_points = valid_points
        self._plot_bounds = (xmin, xmax, ymin, ymax)
        self.plot_status.set(f"Plotted: {expr}   Mode: {'DEG' if self.evaluator.deg_mode else 'RAD'}   invalid points: {err_count}")
        self._redraw_plot()

    def _redraw_plot(self):
        c = self.canvas
        c.delete("all")
        w = max(1, c.winfo_width())
        h = max(1, c.winfo_height())
        pad = 30

        pal = self._palette or {}
        border = pal.get("border", "#CCCCCC")
        grid_color = pal.get("grid", "#DDDDDD")
        axis_color = pal.get("axis", "#666666")
        plot_color = pal.get("accent", "#0B64F4")

        c.configure(bg=pal.get("surface", "#FFFFFF"), highlightbackground=border)

        if not self._plot_points or not self._plot_bounds:
            c.create_rectangle(0, 0, w, h, outline=border)
            return

        xmin, xmax, ymin, ymax = self._plot_bounds
        xr = xmax - xmin
        yr = ymax - ymin
        if xr == 0 or yr == 0:
            return

        def to_canvas(x, y):
            px = pad + (x - xmin) * (w - 2 * pad) / xr
            py = h - (pad + (y - ymin) * (h - 2 * pad) / yr)
            return px, py

        c.create_rectangle(pad, pad, w - pad, h - pad, outline=grid_color)

        if ymin <= 0 <= ymax:
            x0, y0 = to_canvas(xmin, 0); x1, y1 = to_canvas(xmax, 0)
            c.create_line(x0, y0, x1, y1, fill=axis_color)
        if xmin <= 0 <= xmax:
            x0, y0 = to_canvas(0, ymin); x1, y1 = to_canvas(0, ymax)
            c.create_line(x0, y0, x1, y1, fill=axis_color)

        path = []
        for x, y in self._plot_points:
            px, py = to_canvas(x, y)
            if math.isfinite(px) and math.isfinite(py):
                path.append((px, py))
            else:
                if len(path) >= 2:
                    c.create_line(path, fill=plot_color, width=2, smooth=True)
                path = []
        if len(path) >= 2:
            c.create_line(path, fill=plot_color, width=2, smooth=True)

    def apply_theme(self, pal, name):
        self._palette = pal
        self._theme_name = name
        self._redraw_plot()

