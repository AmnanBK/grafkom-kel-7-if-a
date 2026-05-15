"""
control_panel.py
================
Panel kontrol UI aplikasi grafika komputer 2D.

Terdiri dari:
  - Panel kiri  : pemilihan objek, mode (fill/outline), warna, tombol reset
  - Panel bawah : input transformasi (translasi, scaling, rotasi, refleksi, shear)

Desain UI mengikuti prinsip:
  - Bersih dan mudah dipresentasikan
  - Setiap kontrol memiliki label yang jelas
  - Validasi input dasar (numerik) sebelum Apply
  - Feedback visual pada tombol
"""

import tkinter as tk
from tkinter import ttk, colorchooser, messagebox


# ── Konstanta Warna UI ──────────────────────────────────────────────
BG_PANEL      = "#FFFFFF"     # Background panel kontrol
BG_SECTION    = "#F8F9FA"     # Background section/group
BG_BTN        = "#E9ECEF"     # Tombol normal
BG_BTN_HOVER  = "#DEE2E6"     # Tombol hover
BG_BTN_ACTIVE = "#007BFF"     # Tombol aktif/terpilih
BG_BTN_APPLY  = "#28A745"     # Tombol Apply (hijau)
BG_BTN_RESET  = "#DC3545"     # Tombol Reset (merah)
FG_TEXT       = "#212529"     # Teks normal
FG_LABEL      = "#495057"     # Teks label
FG_TITLE      = "#212529"     # Teks judul seksi
BORDER_COLOR  = "#CED4DA"     # Warna border

FONT_TITLE    = ("Consolas", 10, "bold")
FONT_LABEL    = ("Consolas", 9)
FONT_BTN      = ("Consolas", 9, "bold")
FONT_INPUT    = ("Consolas", 10)


class ControlPanel:
    """
    Panel kontrol lengkap untuk aplikasi grafika 2D.

    Callback yang harus dihubungkan dari App (controller):
        on_shape_selected(shape_type: str)
        on_fill_mode_changed(fill_mode: bool)
        on_color_changed(color: str)
        on_transform_applied(params: dict)
        on_reset()
    """

    # Daftar objek yang tersedia
    SHAPE_TYPES = [
        ("Persegi Panjang", "rectangle"),
        ("Persegi",         "square"),
        ("Segitiga",        "triangle"),
        ("Lingkaran",       "circle"),
        ("Elips",           "ellipse"),
    ]

    def __init__(self, root: tk.Tk, callbacks: dict):
        """
        Args:
            root: Window Tkinter utama
            callbacks: Dictionary callback dari App controller
                Keys: 'on_shape', 'on_fill_mode', 'on_color',
                      'on_transform', 'on_reset'
        """
        self.root      = root
        self.callbacks = callbacks
        self.current_fill_color = "#4A90D9"
        self.current_outline_color = "#1A3A5C"

        # State pilihan aktif
        self._selected_shape = tk.StringVar(value="")
        self._fill_mode      = tk.BooleanVar(value=True)

        # Frame induk panel kiri
        self.left_panel = tk.Frame(root, bg=BG_PANEL, width=200)
        self.left_panel.grid(row=0, column=1, sticky="ns")
        self.left_panel.grid_propagate(False)

        # Frame induk panel bawah (transformasi)
        self.bottom_panel = tk.Frame(root, bg=BG_PANEL, height=160)
        self.bottom_panel.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.bottom_panel.grid_propagate(False)

        # Build UI sections
        self._build_shape_section()
        self._build_mode_section()
        self._build_color_section()
        self._build_reset_section()
        self._build_transform_panel()

    # ─────────────────────────────────────────────────────────────────
    # PANEL KIRI — PEMILIHAN OBJEK
    # ─────────────────────────────────────────────────────────────────

    def _build_shape_section(self):
        """Section pemilihan jenis objek primitif."""
        frame = self._make_section(self.left_panel, "PILIH OBJEK")

        self._shape_buttons = {}
        for label, key in self.SHAPE_TYPES:
            btn = tk.Button(
                frame,
                text=f"  {label}",
                anchor="w",
                bg=BG_BTN,
                fg=FG_TEXT,
                font=FONT_BTN,
                relief=tk.FLAT,
                padx=8, pady=5,
                cursor="hand2",
                command=lambda k=key, l=label: self._on_shape_click(k, l),
            )
            btn.pack(fill=tk.X, pady=2)
            self._add_hover(btn)
            self._shape_buttons[key] = btn

    def _on_shape_click(self, shape_key: str, label: str):
        """Handle klik tombol pilihan objek."""
        # Reset highlight semua tombol
        for k, btn in self._shape_buttons.items():
            btn.configure(bg=BG_BTN, fg=FG_TEXT)
        # Highlight tombol yang dipilih
        self._shape_buttons[shape_key].configure(
            bg=BG_BTN_ACTIVE, fg="#FFFFFF"
        )
        self._selected_shape.set(shape_key)
        # Panggil callback
        if 'on_shape' in self.callbacks:
            self.callbacks['on_shape'](shape_key)

    # ─────────────────────────────────────────────────────────────────
    # PANEL KIRI — MODE FILL / OUTLINE
    # ─────────────────────────────────────────────────────────────────

    def _build_mode_section(self):
        """Section pilihan mode render: Fill atau Outline."""
        frame = self._make_section(self.left_panel, "MODE RENDER")

        mode_frame = tk.Frame(frame, bg=BG_SECTION)
        mode_frame.pack(fill=tk.X)

        self._btn_fill = tk.Button(
            mode_frame, text="● Fill",
            bg=BG_BTN_ACTIVE, fg="#FFFFFF",
            font=FONT_BTN, relief=tk.FLAT, padx=8, pady=4,
            cursor="hand2",
            command=lambda: self._on_mode_change(True),
        )
        self._btn_fill.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))

        self._btn_outline = tk.Button(
            mode_frame, text="○ Outline",
            bg=BG_BTN, fg=FG_TEXT,
            font=FONT_BTN, relief=tk.FLAT, padx=8, pady=4,
            cursor="hand2",
            command=lambda: self._on_mode_change(False),
        )
        self._btn_outline.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(2, 0))

    def _on_mode_change(self, fill_mode: bool):
        """Handle perubahan mode fill/outline."""
        self._fill_mode.set(fill_mode)
        if fill_mode:
            self._btn_fill.configure(bg=BG_BTN_ACTIVE, fg="#FFFFFF")
            self._btn_outline.configure(bg=BG_BTN, fg=FG_TEXT)
            # Update preview ke warna fill saat ini
            self._color_preview.configure(
                bg=self.current_fill_color,
                text=f"  {self.current_fill_color}  ",
            )
        else:
            self._btn_fill.configure(bg=BG_BTN, fg=FG_TEXT)
            self._btn_outline.configure(bg=BG_BTN_ACTIVE, fg="#FFFFFF")
            # Update preview ke warna outline saat ini
            self._color_preview.configure(
                bg=self.current_outline_color,
                text=f"  {self.current_outline_color}  ",
            )
        if 'on_fill_mode' in self.callbacks:
            self.callbacks['on_fill_mode'](fill_mode)

    # ─────────────────────────────────────────────────────────────────
    # PANEL KIRI — PILIH WARNA
    # ─────────────────────────────────────────────────────────────────

    def _build_color_section(self):
        """Section pemilihan warna objek."""
        frame = self._make_section(self.left_panel, "WARNA OBJEK")

        self._color_preview = tk.Label(
            frame,
            text=f"  {self.current_fill_color}  ",
            bg=self.current_fill_color,
            fg="#FFFFFF",
            font=FONT_LABEL,
            relief=tk.FLAT,
            padx=4, pady=6,
        )
        self._color_preview.pack(fill=tk.X, pady=(0, 4))

        btn = tk.Button(
            frame,
            text="  Pilih Warna...",
            anchor="w",
            bg=BG_BTN,
            fg=FG_TEXT,
            font=FONT_BTN,
            relief=tk.FLAT,
            padx=8, pady=4,
            cursor="hand2",
            command=self._on_color_pick,
        )
        btn.pack(fill=tk.X)
        self._add_hover(btn)

    def _on_color_pick(self):
        """Buka dialog color picker."""
        # Tentukan warna awal berdasarkan mode aktif
        current_color = self.current_fill_color if self._fill_mode.get() else self.current_outline_color
        
        color_code = colorchooser.askcolor(
            title="Pilih Warna Objek",
            color=current_color,
            parent=self.root,
        )
        if color_code and color_code[1]:
            new_color = color_code[1]
            
            # Simpan ke variabel yang sesuai dengan mode aktif
            if self._fill_mode.get():
                self.current_fill_color = new_color
            else:
                self.current_outline_color = new_color
            
            # Update preview
            self._color_preview.configure(
                bg=new_color,
                text=f"  {new_color}  ",
            )
            
            # Panggil callback dengan mode info
            if 'on_color' in self.callbacks:
                self.callbacks['on_color'](new_color, self._fill_mode.get())

    # ─────────────────────────────────────────────────────────────────
    # PANEL KIRI — TOMBOL RESET
    # ─────────────────────────────────────────────────────────────────

    def _build_reset_section(self):
        """Tombol reset ke posisi asal."""
        frame = tk.Frame(self.left_panel, bg=BG_PANEL)
        frame.pack(fill=tk.X, padx=8, pady=(16, 4))

        btn = tk.Button(
            frame,
            text="↺  RESET TRANSFORMASI",
            bg=BG_BTN_RESET,
            fg="#FFFFFF",
            font=FONT_BTN,
            relief=tk.FLAT,
            padx=8, pady=6,
            cursor="hand2",
            command=self._on_reset,
        )
        btn.pack(fill=tk.X)

    def _on_reset(self):
        """Handle tombol reset."""
        if 'on_reset' in self.callbacks:
            self.callbacks['on_reset']()
        # Kosongkan semua entry field
        self._clear_entries()

    # ─────────────────────────────────────────────────────────────────
    # PANEL BAWAH — INPUT TRANSFORMASI
    # ─────────────────────────────────────────────────────────────────

    def _build_transform_panel(self):
        """Panel transformasi di bagian bawah layar."""
        # Header
        header = tk.Label(
            self.bottom_panel,
            text="TRANSFORMASI",
            bg=BG_PANEL, fg=FG_TITLE,
            font=FONT_TITLE,
            anchor="w",
            padx=8,
        )
        header.pack(fill=tk.X, pady=(6, 2))

        # Container untuk semua input transformasi (horizontal)
        inputs_frame = tk.Frame(self.bottom_panel, bg=BG_PANEL)
        inputs_frame.pack(fill=tk.X, padx=8, pady=4)

        # ── Translasi ────────────────────────────────────────────────
        t_frame = self._make_input_group(inputs_frame, "TRANSLASI")
        self._entry_tx = self._make_labeled_entry(t_frame, "tx (px):", "0")
        self._entry_ty = self._make_labeled_entry(t_frame, "ty (px):", "0")
        t_frame.pack(side=tk.LEFT, padx=(0, 12))

        # ── Rotasi ───────────────────────────────────────────────────
        r_frame = self._make_input_group(inputs_frame, "ROTASI (pivot: centroid)")
        self._entry_angle = self._make_labeled_entry(r_frame, "θ (derajat):", "0")
        r_frame.pack(side=tk.LEFT, padx=(0, 12))

        # ── Scaling ──────────────────────────────────────────────────
        s_frame = self._make_input_group(inputs_frame, "SCALING (pivot: centroid)")
        self._entry_sx = self._make_labeled_entry(s_frame, "sx:", "1")
        self._entry_sy = self._make_labeled_entry(s_frame, "sy:", "1")
        s_frame.pack(side=tk.LEFT, padx=(0, 12))

        # ── Refleksi (opsional) ──────────────────────────────────────
        rf_frame = self._make_input_group(inputs_frame, "REFLEKSI (opsional)")
        self._btn_reflect_x = tk.Button(
            rf_frame, text="Refleksi sb. X",
            bg=BG_BTN, fg=FG_TEXT, font=FONT_BTN,
            relief=tk.FLAT, padx=6, pady=3, cursor="hand2",
            command=lambda: self._on_reflect('x'),
        )
        self._btn_reflect_x.pack(fill=tk.X, pady=2)
        self._btn_reflect_y = tk.Button(
            rf_frame, text="Refleksi sb. Y",
            bg=BG_BTN, fg=FG_TEXT, font=FONT_BTN,
            relief=tk.FLAT, padx=6, pady=3, cursor="hand2",
            command=lambda: self._on_reflect('y'),
        )
        self._btn_reflect_y.pack(fill=tk.X, pady=2)
        rf_frame.pack(side=tk.LEFT, padx=(0, 12))

        # ── Shear (opsional) ─────────────────────────────────────────
        sh_frame = self._make_input_group(inputs_frame, "SHEAR (opsional)")
        self._entry_shx = self._make_labeled_entry(sh_frame, "shx:", "0")
        self._entry_shy = self._make_labeled_entry(sh_frame, "shy:", "0")
        sh_frame.pack(side=tk.LEFT, padx=(0, 12))

        # ── Tombol Apply ─────────────────────────────────────────────
        apply_frame = tk.Frame(inputs_frame, bg=BG_PANEL)
        apply_frame.pack(side=tk.LEFT, padx=(8, 0))
        tk.Button(
            apply_frame,
            text="▶ APPLY",
            bg=BG_BTN_APPLY,
            fg="#FFFFFF",
            font=("Consolas", 11, "bold"),
            relief=tk.FLAT,
            padx=16, pady=18,
            cursor="hand2",
            command=self._on_apply,
        ).pack(expand=True, fill=tk.BOTH)

    def _on_apply(self):
        """Validasi input dan panggil callback transformasi."""
        try:
            params = {
                'tx'    : float(self._entry_tx.get()    or 0),
                'ty'    : float(self._entry_ty.get()    or 0),
                'angle' : float(self._entry_angle.get() or 0),
                'sx'    : float(self._entry_sx.get()    or 1),
                'sy'    : float(self._entry_sy.get()    or 1),
                'shx'   : float(self._entry_shx.get()   or 0),
                'shy'   : float(self._entry_shy.get()   or 0),
            }
        except ValueError:
            messagebox.showerror(
                "Input Tidak Valid",
                "Semua nilai transformasi harus berupa angka.\n"
                "Contoh: tx=20, sy=1.5, θ=45",
                parent=self.root,
            )
            return

        # Validasi faktor skala
        if params['sx'] <= 0 or params['sy'] <= 0:
            messagebox.showerror(
                "Nilai Skala Tidak Valid",
                "Faktor skala (sx, sy) harus lebih besar dari 0.",
                parent=self.root,
            )
            return

        if 'on_transform' in self.callbacks:
            self.callbacks['on_transform'](params)

        # Reset entry ke nilai netral setelah apply
        self._reset_entries_to_neutral()

    def _on_reflect(self, axis: str):
        """Handle tombol refleksi."""
        if 'on_transform' in self.callbacks:
            self.callbacks['on_transform']({'reflect': axis})

    # ─────────────────────────────────────────────────────────────────
    # HELPER — BUILDER UI
    # ─────────────────────────────────────────────────────────────────

    def _make_section(self, parent: tk.Widget, title: str) -> tk.Frame:
        """Buat section dengan judul dan frame konten."""
        wrapper = tk.Frame(parent, bg=BG_PANEL)
        wrapper.pack(fill=tk.X, padx=8, pady=(10, 0))

        tk.Label(
            wrapper, text=title,
            bg=BG_PANEL, fg=FG_LABEL,
            font=("Consolas", 8, "bold"),
            anchor="w",
        ).pack(fill=tk.X, pady=(0, 4))

        inner = tk.Frame(wrapper, bg=BG_SECTION, padx=6, pady=6)
        inner.pack(fill=tk.X)
        return inner

    def _make_input_group(self, parent: tk.Widget, title: str) -> tk.Frame:
        """Buat grup input dengan judul di panel transformasi."""
        frame = tk.Frame(parent, bg=BG_PANEL)
        tk.Label(
            frame, text=title,
            bg=BG_PANEL, fg=FG_LABEL,
            font=("Consolas", 7, "bold"),
            anchor="w",
        ).pack(anchor="w", pady=(0, 2))
        return frame

    def _make_labeled_entry(
        self, parent: tk.Widget, label: str, default: str
    ) -> tk.Entry:
        """Buat pasangan label + entry field."""
        row = tk.Frame(parent, bg=BG_PANEL)
        row.pack(fill=tk.X, pady=1)

        tk.Label(
            row, text=label,
            bg=BG_PANEL, fg=FG_TEXT,
            font=FONT_LABEL, width=10, anchor="w",
        ).pack(side=tk.LEFT)

        entry = tk.Entry(
            row,
            width=7,
            font=FONT_INPUT,
            bg="#FFFFFF",
            fg=FG_TEXT,
            insertbackground=FG_TEXT,
            relief=tk.FLAT,
            bd=4,
        )
        entry.insert(0, default)
        entry.pack(side=tk.LEFT, padx=(4, 0))

        # Pilih semua teks saat entry diklik
        entry.bind("<FocusIn>", lambda e: entry.select_range(0, tk.END))
        # Enter = Apply
        entry.bind("<Return>", lambda e: self._on_apply())
        return entry

    def _add_hover(self, btn: tk.Button):
        """Tambahkan efek hover pada tombol."""
        original_bg = btn.cget('bg')
        btn.bind("<Enter>", lambda e: btn.configure(bg=BG_BTN_HOVER))
        btn.bind("<Leave>", lambda e: btn.configure(bg=original_bg))

    def _clear_entries(self):
        """Kosongkan semua entry dan reset ke nilai netral."""
        self._reset_entries_to_neutral()

    def _reset_entries_to_neutral(self):
        """Reset entry ke nilai netral (tidak mengubah apa-apa jika diapply)."""
        for entry, val in [
            (self._entry_tx, "0"),
            (self._entry_ty, "0"),
            (self._entry_angle, "0"),
            (self._entry_sx, "1"),
            (self._entry_sy, "1"),
            (self._entry_shx, "0"),
            (self._entry_shy, "0"),
        ]:
            entry.delete(0, tk.END)
            entry.insert(0, val)
