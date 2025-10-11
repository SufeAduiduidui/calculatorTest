from PIL import Image
import customtkinter as ctk

class PetWidget(ctk.CTkFrame):
    def __init__(self, master, image_path, size=(64, 64)):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self._src = Image.open(image_path)
        self._size = size
        self._img = ctk.CTkImage(self._src, size=size)
        self._label = ctk.CTkLabel(self, image=self._img, text="")
        self._label.pack()
        self._hover_job = None
        self._hover_i = 0
        self._animating = False
        self._label.bind("<Enter>", self._on_enter)
        self._label.bind("<Leave>", self._on_leave)
        self._label.bind("<Button-1>", self._on_click)

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
        if self._animating:
            return
        self._animating = True
        scales = [1.0, 1.2, 1.35, 1.2, 1.0]
        self._bounce(scales, 0)


    def _bounce(self, scales, idx):
        if idx >= len(scales):
            self._animating = False
            return
        s = scales[idx]
        size = (max(1, int(self._size[0] * s)), max(1, int(self._size[1] * s)))
        self._img = ctk.CTkImage(self._src, size=size)
        self._label.configure(image=self._img)
        self.after(80, lambda: self._bounce(scales, idx + 1))

