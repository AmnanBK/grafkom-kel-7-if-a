"""
app.py
======
Controller utama aplikasi grafika komputer 2D.

Bertanggung jawab untuk:
  - Menginisialisasi semua komponen (View, Control Panel)
  - Menghubungkan callback dari UI ke logika bisnis
  - Mengelola objek aktif (active_shape)
  - Mengkoordinasikan alur: input → transformasi → render

Pola arsitektur: MVC sederhana
  - Model   : BaseShape + TransformState
  - View    : CanvasView
  - Controller: App (file ini)
"""

import tkinter as tk
from tkinter import ttk

from shapes.rectangle import Rectangle, Square
from shapes.shapes import Triangle, Circle, Ellipse
from ui.canvas_view import CanvasView
from ui.control_panel import ControlPanel


# ── Konstanta Aplikasi ──────────────────────────────────────────────
APP_TITLE = "Aplikasi Grafika Komputer 2D"
WIN_WIDTH = 1100
WIN_HEIGHT = 720
WIN_MIN_W = 900
WIN_MIN_H = 600

BG_ROOT = "#F0F2F5"


class App:
    """
    Controller utama aplikasi grafika komputer 2D.

    Alur kerja:
      1. User pilih objek → on_shape_selected() → buat shape baru → render
      2. User pilih fill/outline → on_fill_mode_changed() → update shape → render
      3. User pilih warna → on_color_changed() → update shape → render
      4. User isi nilai transformasi → klik Apply → on_transform_applied()
           → update transform_state → hitung current_vertices → render
      5. User klik Reset → on_reset() → reset transform_state → render
    """

    # Mapping nama shape ke class
    SHAPE_CLASSES = {
        "rectangle": Rectangle,
        "square": Square,
        "triangle": Triangle,
        "circle": Circle,
        "ellipse": Ellipse,
    }

    def __init__(self, root: tk.Tk):
        """
        Inisialisasi seluruh aplikasi.

        Args:
            root: Tkinter root window
        """
        self.root = root
        self._setup_window()

        # State aktif
        self.active_shape = None
        self.current_fill_mode = True
        self.current_color = "#0056b3"

        # Buat frame utama (canvas di kanan, panel kiri, panel bawah)
        self.main_frame = tk.Frame(root, bg=BG_ROOT)
        self.main_frame.pack(expand=True, fill=tk.BOTH)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=0)
        self.main_frame.grid_rowconfigure(1, weight=0)

        # Inisialisasi ControlPanel dengan callback
        self.control_panel = ControlPanel(
            self.main_frame,
            callbacks={
                "on_shape": self.on_shape_selected,
                "on_fill_mode": self.on_fill_mode_changed,
                "on_color": self.on_color_changed,
                "on_transform": self.on_transform_applied,
                "on_reset": self.on_reset,
            },
        )

        # CanvasView dibuat setelah control panel (agar layout benar)
        self.canvas_frame = tk.Frame(self.main_frame, bg=BG_ROOT)
        self.canvas_frame.grid(row=0, column=0, sticky="nsew")

        self.canvas_view = CanvasView(
            self.canvas_frame,
            width=720,
            height=560,
        )
        self.canvas_view.clear()

        # Title bar
        self._build_title_bar()

    def _setup_window(self):
        """Konfigurasi window utama."""
        self.root.title(APP_TITLE)
        self.root.geometry(f"{WIN_WIDTH}x{WIN_HEIGHT}")
        self.root.minsize(WIN_MIN_W, WIN_MIN_H)
        self.root.configure(bg=BG_ROOT)
        # Posisi window di tengah layar
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - WIN_WIDTH) // 2
        y = (self.root.winfo_screenheight() - WIN_HEIGHT) // 2
        self.root.geometry(f"{WIN_WIDTH}x{WIN_HEIGHT}+{x}+{y}")

    def _build_title_bar(self):
        """Buat title bar kustom di bagian atas canvas."""
        title_frame = tk.Frame(self.canvas_frame, bg="#FFFFFF", height=32)
        title_frame.pack(side=tk.TOP, fill=tk.X)
        title_frame.pack_propagate(False)

        tk.Label(
            title_frame,
            text=f"  {APP_TITLE}  —  Mata Kuliah Grafika Komputer",
            bg="#FFFFFF",
            fg="#333333",
            font=("Consolas", 9),
            anchor="w",
        ).pack(side=tk.LEFT, fill=tk.Y, padx=8)

        tk.Label(
            title_frame,
            text="Satu objek aktif pada satu waktu",
            bg="#FFFFFF",
            fg="#666666",
            font=("Consolas", 8),
            anchor="e",
        ).pack(side=tk.RIGHT, fill=tk.Y, padx=8)

    # ─────────────────────────────────────────────────────────────────
    # CALLBACK HANDLERS
    # ─────────────────────────────────────────────────────────────────

    def on_shape_selected(self, shape_type: str):
        """
        Dipanggil ketika user memilih jenis objek baru.

        Membuat instance shape baru di tengah canvas,
        menggantikan objek aktif sebelumnya.

        Args:
            shape_type: Key shape ('rectangle', 'square', dst.)
        """
        ShapeClass = self.SHAPE_CLASSES.get(shape_type)
        if ShapeClass is None:
            return

        # Ambil koordinat tengah canvas
        cx, cy = self.canvas_view.get_canvas_center()

        # Buat shape baru dengan state bersih
        self.active_shape = ShapeClass(
            canvas_cx=cx,
            canvas_cy=cy,
            fill_mode=self.current_fill_mode,
            color=self.current_color,
        )

        # Render ke canvas
        self._render()

    def on_fill_mode_changed(self, fill_mode: bool):
        """
        Dipanggil ketika user mengubah mode render (fill/outline).

        Args:
            fill_mode: True = fill, False = outline
        """
        self.current_fill_mode = fill_mode
        if self.active_shape:
            self.active_shape.set_fill_mode(fill_mode)
            self._render()

    def on_color_changed(self, color: str):
        """
        Dipanggil ketika user memilih warna baru.

        Args:
            color: Kode warna hex (misal '#FF5733')
        """
        self.current_color = color
        if self.active_shape:
            self.active_shape.set_color(color)
            self._render()

    def on_transform_applied(self, params: dict):
        """
        Dipanggil ketika user menekan tombol Apply transformasi.

        Menerapkan transformasi kumulatif ke TransformState shape aktif,
        lalu render ulang.

        Args:
            params: Dictionary berisi parameter transformasi:
                - 'tx', 'ty'    : translasi (float)
                - 'angle'       : rotasi dalam derajat (float)
                - 'sx', 'sy'    : faktor skala (float)
                - 'shx', 'shy'  : shear (float)
                - 'reflect'     : 'x' atau 'y' untuk refleksi
        """
        if not self.active_shape:
            # Tidak ada objek aktif — ingatkan user
            import tkinter.messagebox as mb

            mb.showwarning(
                "Tidak Ada Objek",
                "Pilih objek terlebih dahulu sebelum melakukan transformasi.",
                parent=self.root,
            )
            return

        state = self.active_shape.transform_state

        # Terapkan transformasi sesuai params yang diberikan
        if "reflect" in params:
            # Refleksi — toggle
            if params["reflect"] == "x":
                state.apply_reflection_x()
            elif params["reflect"] == "y":
                state.apply_reflection_y()
        else:
            # Transformasi reguler: translasi, rotasi, scaling, shear
            tx = params.get("tx", 0.0)
            ty = params.get("ty", 0.0)
            angle = params.get("angle", 0.0)
            sx = params.get("sx", 1.0)
            sy = params.get("sy", 1.0)
            shx = params.get("shx", 0.0)
            shy = params.get("shy", 0.0)

            # Terapkan hanya jika ada perubahan (hindari akumulasi noise)
            if tx != 0 or ty != 0:
                state.apply_translation(tx, ty)
            if angle != 0:
                state.apply_rotation(angle)
            if sx != 1.0 or sy != 1.0:
                state.apply_scaling(sx, sy)
            if shx != 0 or shy != 0:
                state.apply_shear(shx, shy)

        self._render()

    def on_reset(self):
        """
        Dipanggil ketika user menekan tombol Reset.
        Mengembalikan objek ke posisi dan ukuran asal.
        """
        if self.active_shape:
            self.active_shape.reset()
            self._render()

    # ─────────────────────────────────────────────────────────────────
    # RENDER
    # ─────────────────────────────────────────────────────────────────

    def _render(self):
        """
        Render ulang canvas dengan objek aktif saat ini.
        Dipanggil setelah setiap perubahan state.
        """
        if self.active_shape:
            self.canvas_view.render(self.active_shape)
        else:
            self.canvas_view.clear()
