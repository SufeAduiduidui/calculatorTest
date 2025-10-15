# calculator_app/ui/pet_widget.py
from PIL import Image, ImageSequence, ImageTk
from .sound_player import play as play_sound
import customtkinter as ctk
from typing import Callable, Optional, Sequence


class PetWidget(ctk.CTkFrame):
    def __init__(self, master, image_path, size=(64, 64), on_click: Optional[Callable[[], None]] = None,
                 on_triple_click: Optional[Callable[[], None]] = None, sound_path: Optional[str] = "assets/cat.mp3"):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self._size = size
        self._on_click_cb = on_click
        self._on_triple_cb = on_triple_click
        self._sound_path = sound_path

        self._label = ctk.CTkLabel(self, text="")
        self._label.pack()
        self._hover_job = None
        self._hover_i = 0
        self._animating = False
        self._enabled = True

        self._frame_job = None
        self._anim_frames: Sequence[ImageTk.PhotoImage] = []
        self._anim_durations: Sequence[int] = []
        self._frame_index = 0
        self._is_gif = False
        self._static_image: Optional[Image.Image] = None
        self._base_ctk_image: Optional[ctk.CTkImage] = None
        self._bounce_image: Optional[ctk.CTkImage] = None

        self.set_image(image_path, size=size)

        self._label.bind("<Enter>", self._on_enter)
        self._label.bind("<Leave>", self._on_leave)
        self._label.bind("<Button-1>", self._on_click)
        self._label.bind("<Triple-Button-1>", self._on_triple)

    def set_image(self, image_path: str, size: Optional[tuple[int, int]] = None,
                  sound_path: Optional[str] = None) -> None:
        if size:
            self._size = size
        if sound_path is not None:
            self._sound_path = sound_path

        if self._frame_job:
            try:
                self.after_cancel(self._frame_job)
            except Exception:
                pass
            self._frame_job = None

        self._is_gif = False
        self._anim_frames = []
        self._anim_durations = []
        self._frame_index = 0

        img = Image.open(image_path)
        if getattr(img, "is_animated", False) and getattr(img, "n_frames", 1) > 1:
            self._is_gif = True
            frames = []
            durations = []
            for frame in ImageSequence.Iterator(img):
                frame = frame.convert("RGBA")
                resized = frame.resize(self._size, Image.LANCZOS)
                frames.append(ImageTk.PhotoImage(resized))
                durations.append(max(40, frame.info.get("duration", 120)))
            self._anim_frames = frames
            self._anim_durations = durations
            self._frame_index = 0
            self._label.configure(image=self._anim_frames[0])
            self._label.image = self._anim_frames[0]
            self._schedule_next_frame()
            self._static_image = None
            self._base_ctk_image = None
        else:
            self._static_image = img.convert("RGBA")
            self._base_ctk_image = ctk.CTkImage(self._static_image, size=self._size)
            self._label.configure(image=self._base_ctk_image)
            self._label.image = None
        img.close()

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = bool(enabled)

    def _schedule_next_frame(self) -> None:
        if not self._is_gif or not self._anim_frames:
            return
        duration = self._anim_durations[self._frame_index % len(self._anim_durations)]
        self._frame_job = self.after(duration, self._advance_frame)

    def _advance_frame(self) -> None:
        if not self._is_gif or not self._anim_frames:
            return
        self._frame_index = (self._frame_index + 1) % len(self._anim_frames)
        frame = self._anim_frames[self._frame_index]
        self._label.configure(image=frame)
        self._label.image = frame
        self._schedule_next_frame()

    def _on_triple(self, _event=None):
        if not self._enabled:
            return
        if callable(self._on_triple_cb):
            try:
                self._on_triple_cb()
            except Exception:
                pass
        else:
            try:
                self.event_generate("<<PetTripleClick>>")
            except Exception:
                pass

    def _on_enter(self, _event=None):
        if self._hover_job is None:
            self._hover_i = 0
            self._hover_job = self.after(50, self._wiggle)

    def _on_leave(self, _event=None):
        if self._hover_job:
            self.after_cancel(self._hover_job)
            self._hover_job = None
        self._label.pack_configure(padx=0)

    def _wiggle(self):
        offsets = [0, 4, 8, 4, 0, -4, -8, -4]
        o = offsets[self._hover_i % len(offsets)]
        base = 8
        if o >= 0:
            padx = (base + o, base)
        else:
            padx = (base, base + (-o))
        self._label.pack_configure(padx=padx)
        self._hover_i += 1
        self._hover_job = self.after(70, self._wiggle)

    def _on_click(self, _event=None):
        if not self._enabled or self._animating:
            return
        if callable(self._on_click_cb):
            try:
                self._on_click_cb()
            except Exception:
                pass
        if self._sound_path:
            try:
                play_sound(self._sound_path)
            except Exception:
                pass
        if self._is_gif:
            return
        self._animating = True
        scales = [1.0, 1.2, 1.35, 1.2, 1.0]
        self._bounce(scales, 0)

    def _bounce(self, scales, idx):
        if idx >= len(scales) or self._static_image is None:
            self._animating = False
            if self._base_ctk_image:
                self._label.configure(image=self._base_ctk_image)
            self._bounce_image = None
            return
        s = scales[idx]
        size = (max(1, int(self._size[0] * s)), max(1, int(self._size[1] * s)))
        resized = self._static_image.resize(size, Image.LANCZOS)
        self._bounce_image = ctk.CTkImage(resized, size=size)
        self._label.configure(image=self._bounce_image)
        self.after(80, lambda: self._bounce(scales, idx + 1))
