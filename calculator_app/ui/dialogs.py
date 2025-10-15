from __future__ import annotations

import tkinter as tk
import tkinter.font as tkfont
from typing import Mapping, Optional, Tuple


def _resolve_palette(palette: Optional[Mapping[str, str]]) -> Tuple[str, str, str]:
    pal = palette or {}
    surface = pal.get("surface", "#FFFFFF")
    text = pal.get("text", "#000000")
    border = pal.get("border", "#D1D1D6")
    return surface, text, border


def _rounded_polygon(canvas: tk.Canvas, x0: float, y0: float, x1: float, y1: float, radius: float,
                     **kwargs) -> int:
    radius = max(4.0, min(radius, (x1 - x0) / 2, (y1 - y0) / 2))
    points = [
        x0 + radius, y0,
        x1 - radius, y0,
        x1, y0,
        x1, y0 + radius,
        x1, y1 - radius,
        x1, y1,
        x1 - radius, y1,
        x0 + radius, y1,
        x0, y1,
        x0, y1 - radius,
        x0, y0 + radius,
        x0, y0,
    ]
    return canvas.create_polygon(
        points,
        smooth=True,
        splinesteps=36,
        **kwargs,
    )


def show_cat_bubble(
    anchor_widget: tk.Widget,
    message: str,
    palette: Optional[Mapping[str, str]] = None,
    *,
    direction: str = "left",
    duration_ms: int = 2400,
    align_widget: Optional[tk.Widget] = None,
    align_offset: float = 0.0,
    wrap_width: int = 260,
) -> Optional[tk.Toplevel]:
    """Draw a lightweight speech bubble anchored to `anchor_widget`."""
    if anchor_widget is None or not anchor_widget.winfo_exists():
        return None

    parent = anchor_widget.winfo_toplevel()
    try:
        parent.update_idletasks()
        anchor_widget.update_idletasks()
    except Exception:
        pass

    surface_color, text_color, border_color = _resolve_palette(palette)
    direction = (direction or "left").lower()
    if direction not in {"left", "right", "up", "down"}:
        direction = "left"

    transparent_color = "#010101"
    bubble = tk.Toplevel(parent)
    bubble.withdraw()
    bubble.overrideredirect(True)
    bubble.attributes("-topmost", True)
    bubble.configure(bg=transparent_color, padx=0, pady=0)
    try:
        bubble.attributes("-transparentcolor", transparent_color)
    except tk.TclError:
        pass

    canvas = tk.Canvas(
        bubble,
        bg=transparent_color,
        highlightthickness=0,
        bd=0,
    )
    canvas.pack(fill="both", expand=True)

    font = tkfont.Font(family="Microsoft YaHei UI", size=13)
    padding_x = 22
    padding_y = 16
    wrap_width = max(200, wrap_width)

    text_id = canvas.create_text(
        padding_x,
        padding_y,
        text=message,
        fill=text_color,
        font=font,
        width=wrap_width,
        anchor="nw",
    )
    canvas.update_idletasks()

    bbox = canvas.bbox(text_id)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    arrow_w = 24
    arrow_h = 20
    body_width = text_width + padding_x * 2
    body_height = text_height + padding_y * 2
    radius = min(18.0, body_height / 2, body_width / 2)
    arrow_tip_y: Optional[float] = None

    if direction == "left":
        total_width = body_width + arrow_w
        total_height = body_height + arrow_h
        body_x0 = 0.0
        body_y0 = 0.0
        body_x1 = body_width
        body_y1 = body_height
        base_upper = body_y1 - arrow_h * 0.6
        base_lower = body_y1 - arrow_h * 0.15
        tip_y = body_y1 + arrow_h * 0.6
        arrow_points = [
            body_x1 - radius / 2,
            base_upper,
            body_x1 + arrow_w,
            tip_y,
            body_x1 - radius / 2,
            base_lower,
        ]
        arrow_tip_y = tip_y
    elif direction == "right":
        total_width = body_width + arrow_w
        total_height = body_height + arrow_h
        body_x0 = arrow_w
        body_y0 = 0.0
        body_x1 = body_x0 + body_width
        body_y1 = body_height
        base_upper = body_y1 - arrow_h * 0.6
        base_lower = body_y1 - arrow_h * 0.15
        tip_y = body_y1 + arrow_h * 0.6
        arrow_points = [
            body_x0 + radius / 2,
            base_lower,
            body_x0 - arrow_w,
            tip_y,
            body_x0 + radius / 2,
            base_upper,
        ]
        arrow_tip_y = tip_y
    elif direction == "up":
        total_width = max(body_width, arrow_w + 12)
        total_height = body_height + arrow_h
        body_x0 = (total_width - body_width) / 2
        body_y0 = arrow_h
        body_x1 = body_x0 + body_width
        body_y1 = body_y0 + body_height
        mid_x = total_width / 2
        arrow_points = [
            mid_x - arrow_w / 2,
            arrow_h,
            mid_x,
            0,
            mid_x + arrow_w / 2,
            arrow_h,
        ]
    else:  # down
        total_width = max(body_width, arrow_w + 12)
        total_height = body_height + arrow_h
        body_x0 = (total_width - body_width) / 2
        body_y0 = 0.0
        body_x1 = body_x0 + body_width
        body_y1 = body_height
        mid_x = total_width / 2
        tip_y = body_y1 + arrow_h
        arrow_points = [
            mid_x - arrow_w / 2,
            body_y1,
            mid_x,
            tip_y,
            mid_x + arrow_w / 2,
            body_y1,
        ]
        arrow_tip_y = tip_y

    canvas.config(width=total_width, height=total_height)

    text_offset_x = body_x0 + padding_x
    text_offset_y = body_y0 + padding_y
    canvas.coords(text_id, text_offset_x, text_offset_y)

    body = _rounded_polygon(
        canvas,
        body_x0,
        body_y0,
        body_x1,
        body_y1,
        radius,
        fill=surface_color,
        outline=border_color,
        width=1,
    )
    canvas.tag_lower(body, text_id)
    canvas.create_polygon(
        arrow_points,
        smooth=False,
        fill=surface_color,
        outline=border_color,
        width=1,
    )

    bubble.update_idletasks()

    anchor_x = anchor_widget.winfo_rootx()
    anchor_y = anchor_widget.winfo_rooty()
    anchor_w = max(anchor_widget.winfo_width(), 1)
    anchor_h = max(anchor_widget.winfo_height(), 1)

    bubble_w = bubble.winfo_width()
    bubble_h = bubble.winfo_height()
    margin = 12
    anchor_center_x = anchor_x + anchor_w / 2
    anchor_center_y = anchor_y + anchor_h / 2
    if align_widget and align_widget.winfo_exists():
        try:
            align_widget.update_idletasks()
            align_center = align_widget.winfo_rooty() + align_widget.winfo_height() / 2
            anchor_center_y = align_center + align_offset
        except Exception:
            pass

    if direction == "left":
        x = anchor_x - bubble_w - margin
        if arrow_tip_y is not None:
            target_tip = anchor_y + anchor_h * 0.65
            y = target_tip - arrow_tip_y
        else:
            y = anchor_center_y - bubble_h / 2
    elif direction == "right":
        x = anchor_x + anchor_w + margin
        if arrow_tip_y is not None:
            target_tip = anchor_y + anchor_h * 0.65
            y = target_tip - arrow_tip_y
        else:
            y = anchor_center_y - bubble_h / 2
    elif direction == "up":
        x = anchor_center_x - bubble_w / 2
        y = anchor_center_y - bubble_h / 2 - anchor_h / 2 - margin
    else:
        x = anchor_center_x - bubble_w / 2
        if arrow_tip_y is not None:
            target_tip = anchor_y + anchor_h + margin
            y = target_tip - arrow_tip_y
        else:
            y = anchor_center_y + anchor_h / 2 + margin - bubble_h / 2

    try:
        screen_w = bubble.winfo_screenwidth()
        screen_h = bubble.winfo_screenheight()
        x = max(8, min(x, screen_w - bubble_w - 8))
        y = max(8, min(y, screen_h - bubble_h - 8))
    except Exception:
        pass

    bubble.geometry(f"{bubble_w}x{bubble_h}+{int(x)}+{int(y)}")
    bubble.deiconify()

    if duration_ms > 0:
        bubble.after(duration_ms, bubble.destroy)

    return bubble
