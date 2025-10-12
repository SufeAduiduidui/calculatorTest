import math
import tkinter as tk
import customtkinter as ctk


from .sound_player import play as play_sound

from ..core.safe_eval import SafeEvaluator

class PlotPage(ctk.CTkFrame):
    def __init__(self, master, evaluator: SafeEvaluator, palette, theme_name):
        super().__init__(master, corner_radius=12)
        self.evaluator = evaluator
        self._palette = palette
        self._theme_name = theme_name
        self._plot_points = []
        self._plot_bounds = None
        self._build()

    # ---- Plot Tab ------------------------------------------------------------
    def _build(self):
        frame = self

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

        self.apply_theme(self._palette, self._theme_name)

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
            self._redraw_plot()
            return

        ymin = min(y for _, y in valid_points)
        ymax = max(y for _, y in valid_points)
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

        pal = self._palette
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

