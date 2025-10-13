import tkinter as tk
import tkinter.font as tkfont
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
        self._data_bounds = None
        self._query_point = None
        self._suppress_scroll = False
        self._plot_container = None
        self._zoom_frame = None
        self._x_scroll = None
        self._y_scroll = None

        self._build()

    def _set_scrollbar_state(self, scrollbar, state):
        if scrollbar is None:
            return
        try:
            scrollbar.configure(state=state)
        except tk.TclError:
            # Tk scrollbars do not expose a "state" option; ignore if unsupported.
            pass

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

        self.qx_var = tk.StringVar(value="0")
        ctk.CTkLabel(ctrl, text="x =").pack(side="left", padx=(12, 4))
        qx_entry = ctk.CTkEntry(ctrl, textvariable=self.qx_var, width=100)
        qx_entry.pack(side="left", padx=4)
        ctk.CTkButton(ctrl, text="Eval", command=self.eval_point).pack(side="left", padx=6)
        qx_entry.bind("<Return>", lambda e: self.eval_point())

        self.qy_var = tk.StringVar(value="")
        ctk.CTkLabel(frame, textvariable=self.qy_var).pack(anchor="w", padx=10)


        self.plot_status = tk.StringVar(value="")
        ctk.CTkLabel(frame, textvariable=self.plot_status).pack(anchor="w", padx=10)

        canvas_frame = ctk.CTkFrame(frame, corner_radius=12)
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)
        canvas_frame.grid_columnconfigure(1, weight=1)
        canvas_frame.grid_rowconfigure(0, weight=1)

        self._y_scroll = tk.Scrollbar(canvas_frame, orient="vertical", command=self._on_yscroll)
        self._y_scroll.grid(row=0, column=0, sticky="ns", padx=(6, 0), pady=6)

        self._plot_container = ctk.CTkFrame(canvas_frame, corner_radius=8)
        self._plot_container.grid(row=0, column=1, sticky="nsew", padx=(0, 6), pady=6)
        self._plot_container.grid_columnconfigure(0, weight=1)
        self._plot_container.grid_rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(self._plot_container, bg="white", highlightthickness=1)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        self._x_scroll = tk.Scrollbar(canvas_frame, orient="horizontal", command=self._on_xscroll)
        self._x_scroll.grid(row=1, column=1, sticky="ew", padx=(0, 6), pady=(0, 6))

        self._zoom_frame = ctk.CTkFrame(self._plot_container, corner_radius=8)
        zoom_in = ctk.CTkButton(self._zoom_frame, text="+", width=28, height=28, command=lambda: self._zoom(0.7))
        zoom_out = ctk.CTkButton(self._zoom_frame, text="-", width=28, height=28, command=lambda: self._zoom(1.3))
        zoom_in.grid(row=0, column=0, padx=2, pady=2)
        zoom_out.grid(row=0, column=1, padx=2, pady=2)
        self.after(0, self._position_zoom_controls)

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

        self.canvas.update_idletasks()
        cw = max(1, self.canvas.winfo_width())
        samples = max(400, min(1200, int(cw)))
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
        self._data_bounds = (xmin, xmax, ymin, ymax)
        self.plot_status.set(
            f"Plotted: {expr}   Mode: {'DEG' if self.evaluator.deg_mode else 'RAD'}   invalid points: {err_count}")
        self._redraw_plot()

    def eval_point(self):
        s = self.qx_var.get().strip()
        try:
            x = float(s)
            expr = self.func_expr.get().strip()
            y = self.evaluator.evaluate(expr, variables={"x": x})
            if not isinstance(y, (int, float)) or not math.isfinite(y):
                raise ValueError("Invalid result")
            self._query_point = (x, float(y))
            self.qy_var.set(f"f({x}) = {y}")
            self._redraw_plot()
        except Exception as e:
            self._query_point = None
            self.qy_var.set(f"Error: {e}")

    def _redraw_plot(self):
        c = self.canvas
        c.delete("all")
        w = max(1, c.winfo_width())
        h = max(1, c.winfo_height())
        base_pad = 30
        pad_left = base_pad
        pad_right = base_pad
        pad_top = base_pad
        pad_bottom = base_pad

        pal = self._palette or {}
        border = pal.get("border", "#CCCCCC")
        grid_color = pal.get("grid", "#DDDDDD")
        axis_color = pal.get("axis", "#666666")
        plot_color = pal.get("accent", "#0B64F4")
        text_color = pal.get("subtext", "#6C6C70")

        c.configure(bg=pal.get("surface", "#FFFFFF"), highlightbackground=border)

        if not self._plot_points or not self._plot_bounds:
            c.create_rectangle(0, 0, w, h, outline=border)
            self._sync_scrollbars()
            return

        xmin, xmax, ymin, ymax = self._plot_bounds
        xr = xmax - xmin
        yr = ymax - ymin
        if xr == 0 or yr == 0:
            self._sync_scrollbars()
            return

        def nice_step(a, b, target):
            rng = b - a
            if rng <= 0:
                return 1.0
            raw = rng / max(1, target)
            exp = math.floor(math.log10(raw)) if raw > 0 else 0
            base = raw / (10 ** exp)
            for m in (1, 2, 5, 10):
                if base <= m:
                    return m * (10 ** exp)
            return 10 * (10 ** exp)

        def fmt(v):
            if abs(v) < 1e-9:
                v = 0.0
            if abs(v - round(v)) < 1e-9:
                return str(int(round(v)))
            return f"{v:.6g}"

        xstep = nice_step(xmin, xmax, 8)
        ystep = nice_step(ymin, ymax, 8)

        xticks = []
        xt = math.ceil(xmin / xstep) * xstep
        cnt = 0
        while xt <= xmax and cnt < 1000:
            xticks.append(xt)
            xt += xstep
            cnt += 1

        yticks = []
        yt = math.ceil(ymin / ystep) * ystep
        cnt = 0
        while yt <= ymax and cnt < 1000:
            yticks.append(yt)
            yt += ystep
            cnt += 1

        if yticks:
            tick_font = tkfont.nametofont("TkDefaultFont")
            max_width = max(tick_font.measure(fmt(v)) for v in yticks)
            pad_left = max(pad_left, max_width + 12)

        plot_width = w - pad_left - pad_right
        plot_height = h - pad_top - pad_bottom
        if plot_width <= 0 or plot_height <= 0:
            self._sync_scrollbars()
            return

        def to_canvas(x, y):
            px = pad_left + (x - xmin) * plot_width / xr
            py = h - pad_bottom - (y - ymin) * plot_height / yr
            return px, py

        c.create_rectangle(pad_left, pad_top, w - pad_right, h - pad_bottom, outline=grid_color)

        if ymin <= 0 <= ymax:
            x0, y0 = to_canvas(xmin, 0)
            x1, y1 = to_canvas(xmax, 0)
            c.create_line(x0, y0, x1, y1, fill=axis_color)
        if xmin <= 0 <= xmax:
            x0, y0 = to_canvas(0, ymin)
            x1, y1 = to_canvas(0, ymax)
            c.create_line(x0, y0, x1, y1, fill=axis_color)

        for xt in xticks:
            px, _ = to_canvas(xt, ymin)
            c.create_line(px, h - pad_bottom, px, h - pad_bottom + 4, fill=axis_color)
            c.create_text(px, h - pad_bottom + 12, text=fmt(xt), fill=text_color, anchor="n")

        for yt in yticks:
            _, py = to_canvas(xmin, yt)
            c.create_line(pad_left - 4, py, pad_left, py, fill=axis_color)
            c.create_text(pad_left - 6, py, text=fmt(yt), fill=text_color, anchor="e")

        def points_close(a, b, tol=1e-6):
            return abs(a[0] - b[0]) <= tol and abs(a[1] - b[1]) <= tol

        def clip_segment(p0, p1):
            x0, y0 = p0
            x1, y1 = p1
            dx = x1 - x0
            dy = y1 - y0
            t0, t1 = 0.0, 1.0
            clip_tests = (
                (-dx, x0 - xmin),
                (dx, xmax - x0),
                (-dy, y0 - ymin),
                (dy, ymax - y0),
            )
            for p, q in clip_tests:
                if p == 0:
                    if q < 0:
                        return None
                    continue
                t = q / p
                if p < 0:
                    if t > t1:
                        return None
                    if t > t0:
                        t0 = t
                else:
                    if t < t0:
                        return None
                    if t < t1:
                        t1 = t
            if t0 > t1:
                return None
            sx = x0 + t0 * dx
            sy = y0 + t0 * dy
            ex = x0 + t1 * dx
            ey = y0 + t1 * dy
            return (sx, sy), (ex, ey)

        filtered_points = [
            (float(x), float(y))
            for x, y in self._plot_points
            if isinstance(x, (int, float))
            and isinstance(y, (int, float))
            and math.isfinite(x)
            and math.isfinite(y)
        ]

        path = []

        def flush_path():
            nonlocal path
            if len(path) >= 2:
                flat = []
                for a, b in path:
                    flat.extend([a, b])
                c.create_line(flat, fill=plot_color, width=2, smooth=True)
            path = []

        for p0, p1 in zip(filtered_points, filtered_points[1:]):
            seg = clip_segment(p0, p1)
            if not seg:
                flush_path()
                continue
            (sx, sy), (ex, ey) = seg
            start_canvas = to_canvas(sx, sy)
            end_canvas = to_canvas(ex, ey)
            if not all(math.isfinite(v) for v in (*start_canvas, *end_canvas)):
                flush_path()
                continue
            if not path:
                path.append(start_canvas)
            elif not points_close(path[-1], start_canvas):
                flush_path()
                path.append(start_canvas)
            if not points_close(path[-1], end_canvas):
                path.append(end_canvas)

        flush_path()

        qp = getattr(self, "_query_point", None)
        if qp is not None:
            qx, qy = qp
            if isinstance(qx, (int, float)) and isinstance(qy, (int, float)) and math.isfinite(qx) and math.isfinite(
                    qy):
                px, py = to_canvas(qx, qy)
                r = 4
                c.create_oval(px - r, py - r, px + r, py + r, fill=plot_color, outline=plot_color)
                c.create_text(px + 8, py - 8, text=f"({fmt(qx)},{fmt(qy)})", fill=pal.get("text", "#000000"),
                              anchor="sw")

        self._sync_scrollbars()

    def apply_theme(self, pal, name):
        self._palette = pal
        self._theme_name = name
        self._redraw_plot()

    def _position_zoom_controls(self):
        if not self._zoom_frame or not self._plot_container:
            return
        self._zoom_frame.place(relx=1.0, rely=0.0, x=-12, y=12, anchor="ne")

    def _on_canvas_configure(self, event):
        self._position_zoom_controls()
        self._redraw_plot()

    def _zoom(self, factor):
        if not self._plot_bounds or not self._data_bounds:
            return

        xmin, xmax, ymin, ymax = self._plot_bounds
        dx = xmax - xmin
        dy = ymax - ymin
        if dx <= 0 or dy <= 0:
            return

        data_xmin, data_xmax, data_ymin, data_ymax = self._data_bounds
        base_dx = max(data_xmax - data_xmin, 1e-9)
        base_dy = max(data_ymax - data_ymin, 1e-9)

        new_dx = dx * factor
        new_dy = dy * factor

        min_dx = base_dx / 500 if base_dx > 0 else dx
        min_dy = base_dy / 500 if base_dy > 0 else dy

        new_dx = max(min_dx, min(new_dx, base_dx))
        new_dy = max(min_dy, min(new_dy, base_dy))

        cx = (xmin + xmax) / 2
        cy = (ymin + ymax) / 2

        new_xmin = cx - new_dx / 2
        new_xmax = cx + new_dx / 2
        new_ymin = cy - new_dy / 2
        new_ymax = cy + new_dy / 2

        if new_dx >= base_dx:
            new_xmin, new_xmax = data_xmin, data_xmax
        else:
            if new_xmin < data_xmin:
                shift = data_xmin - new_xmin
                new_xmin += shift
                new_xmax += shift
            if new_xmax > data_xmax:
                shift = new_xmax - data_xmax
                new_xmin -= shift
                new_xmax -= shift

        if new_dy >= base_dy:
            new_ymin, new_ymax = data_ymin, data_ymax
        else:
            if new_ymin < data_ymin:
                shift = data_ymin - new_ymin
                new_ymin += shift
                new_ymax += shift
            if new_ymax > data_ymax:
                shift = new_ymax - data_ymax
                new_ymin -= shift
                new_ymax -= shift

        self._plot_bounds = (new_xmin, new_xmax, new_ymin, new_ymax)
        self._redraw_plot()

    def _sync_scrollbars(self):
        if self._x_scroll is None or self._y_scroll is None:
            return

        if not self._plot_bounds or not self._data_bounds:
            self._suppress_scroll = True
            try:
                self._x_scroll.set(0.0, 1.0)
                self._y_scroll.set(0.0, 1.0)
            finally:
                self._suppress_scroll = False
            self._set_scrollbar_state(self._x_scroll, "disabled")
            self._set_scrollbar_state(self._y_scroll, "disabled")
            return

        data_xmin, data_xmax, data_ymin, data_ymax = self._data_bounds
        xmin, xmax, ymin, ymax = self._plot_bounds

        dx = data_xmax - data_xmin
        dy = data_ymax - data_ymin

        if dx <= 0:
            x_first, x_last = 0.0, 1.0
            self._set_scrollbar_state(self._x_scroll, "disabled")
        else:
            x_first = max(0.0, min(1.0, (xmin - data_xmin) / dx))
            x_last = max(0.0, min(1.0, (xmax - data_xmin) / dx))
            self._set_scrollbar_state(self._x_scroll, "normal")

        if dy <= 0:
            y_first, y_last = 0.0, 1.0
            self._set_scrollbar_state(self._y_scroll, "disabled")
        else:
            # invert because scrollbar top corresponds to highest y
            y_first = max(0.0, min(1.0, (data_ymax - ymax) / dy))
            y_last = max(0.0, min(1.0, (data_ymax - ymin) / dy))
            self._set_scrollbar_state(self._y_scroll, "normal")

        self._suppress_scroll = True
        try:
            self._x_scroll.set(x_first, x_last)
            self._y_scroll.set(y_first, y_last)
        finally:
            self._suppress_scroll = False

    def _on_xscroll(self, *args):
        if self._suppress_scroll or not self._plot_bounds or not self._data_bounds:
            return

        xmin, xmax, ymin, ymax = self._plot_bounds
        data_xmin, data_xmax, _, _ = self._data_bounds
        dx = data_xmax - data_xmin
        vw = xmax - xmin
        if dx <= vw or dx <= 0:
            return

        if args[0] == "moveto":
            fraction = float(args[1])
            fraction = max(0.0, min(1.0, fraction))
            new_xmin = data_xmin + fraction * dx
            new_xmax = new_xmin + vw
        elif args[0] == "scroll":
            count = int(args[1])
            step = 0.05 if args[2] == "units" else 0.2
            delta = count * step * (dx - vw)
            new_xmin = xmin + delta
            new_xmax = xmax + delta
        else:
            return

        if new_xmin < data_xmin:
            new_xmin = data_xmin
            new_xmax = new_xmin + vw
        if new_xmax > data_xmax:
            new_xmax = data_xmax
            new_xmin = new_xmax - vw

        self._plot_bounds = (new_xmin, new_xmax, ymin, ymax)
        self._redraw_plot()

    def _on_yscroll(self, *args):
        if self._suppress_scroll or not self._plot_bounds or not self._data_bounds:
            return

        xmin, xmax, ymin, ymax = self._plot_bounds
        _, _, data_ymin, data_ymax = self._data_bounds
        dy = data_ymax - data_ymin
        vh = ymax - ymin
        if dy <= vh or dy <= 0:
            return

        if args[0] == "moveto":
            fraction = float(args[1])
            fraction = max(0.0, min(1.0, fraction))
            new_ymax = data_ymax - fraction * dy
            new_ymin = new_ymax - vh
        elif args[0] == "scroll":
            count = int(args[1])
            step = 0.05 if args[2] == "units" else 0.2
            delta = count * step * (dy - vh)
            new_ymax = ymax - delta
            new_ymin = ymin - delta
        else:
            return

        if new_ymax > data_ymax:
            new_ymax = data_ymax
            new_ymin = new_ymax - vh
        if new_ymin < data_ymin:
            new_ymin = data_ymin
            new_ymax = new_ymin + vh

        self._plot_bounds = (xmin, xmax, new_ymin, new_ymax)
        self._redraw_plot()
