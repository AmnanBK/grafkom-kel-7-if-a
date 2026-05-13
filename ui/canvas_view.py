"""
canvas_view.py
==============
Modul rendering — bertanggung jawab menampilkan objek ke Tkinter Canvas.

Prinsip rendering:
  - Menerima vertices (list of (x,y)) dari shape yang sudah ditransformasi
  - Me-render objek sebagai polygon Tkinter dari vertices tersebut
  - Canvas di-clear dan di-render ulang setiap kali ada perubahan (simple redraw)
  - Menampilkan informasi bantu: garis sumbu, centroid marker, label info

Catatan sistem koordinat:
  Tkinter Canvas menggunakan sistem koordinat layar (Y ke bawah).
  Semua koordinat yang diterima dari shape sudah dalam sistem ini,
  sehingga tidak perlu konversi tambahan.
"""

import math
import tkinter as tk
from shapes.base_shape import BaseShape


# ── Konstanta Visual ────────────────────────────────────────────────
CANVAS_BG         = "#FFFFFF"   # Warna latar canvas (white)
AXIS_COLOR        = "#DEE2E6"   # Warna garis bantu sumbu
AXIS_DASH         = (4, 6)      # Pola putus-putus garis bantu
CENTROID_COLOR    = "#E83E8C"   # Warna marker centroid
CENTROID_RADIUS   = 4           # Radius marker centroid (pixel)
INFO_COLOR        = "#6C757D"   # Warna teks info di canvas
INFO_FONT         = ("Consolas", 9)
LABEL_COLOR       = "#343A40"   # Warna label nama objek
LABEL_FONT        = ("Consolas", 11, "bold")


class CanvasView:
    """
    Komponen view untuk merender objek grafika ke Tkinter Canvas.

    Bertanggung jawab untuk:
      - Merender shape aktif dari vertices yang sudah ditransformasi
      - Menggambar elemen bantu (sumbu, centroid marker, grid)
      - Menampilkan informasi transformasi aktif di canvas
      - Membersihkan canvas saat ganti objek
    """

    def __init__(self, parent: tk.Widget, width: int = 700, height: int = 520):
        """
        Args:
            parent: Widget Tkinter induk (Frame atau root)
            width: Lebar canvas dalam pixel
            height: Tinggi canvas dalam pixel
        """
        self.width  = width
        self.height = height
        self.cx     = width  / 2   # titik tengah canvas X
        self.cy     = height / 2   # titik tengah canvas Y

        # Buat Tkinter Canvas widget
        self.canvas = tk.Canvas(
            parent,
            width=width,
            height=height,
            bg=CANVAS_BG,
            highlightthickness=1,
            highlightbackground="#CED4DA",
            cursor="crosshair",
        )
        self.canvas.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Gambar elemen statis (sumbu bantu)
        self._draw_background()

        # Tag canvas item untuk objek aktif (agar mudah dihapus)
        self._shape_tag   = "active_shape"
        self._overlay_tag = "overlay"

    # ─────────────────────────────────────────────────────────────────
    # RENDERING UTAMA
    # ─────────────────────────────────────────────────────────────────

    def render(self, shape: BaseShape):
        """
        Render ulang seluruh canvas dengan shape aktif.

        Alur:
          1. Hapus semua elemen shape lama
          2. Gambar background (grid & sumbu)
          3. Render shape dari current_vertices
          4. Gambar overlay (centroid, info)

        Args:
            shape: Objek BaseShape yang akan dirender
        """
        # Hapus elemen lama
        self.canvas.delete(self._shape_tag)
        self.canvas.delete(self._overlay_tag)

        # Ambil konfigurasi render dari shape
        config   = shape.get_render_config()
        vertices = config['vertices']

        if len(vertices) < 2:
            return

        # ── Manual Rasterization ──────────────────────────────────────
        if config['fill_mode']:
            # 1. Fill menggunakan Scanline Fill Algorithm
            self._render_scanline_fill(vertices, config['fill'])
            # 2. Gambar tepi menggunakan Bresenham
            self._render_bresenham_outline(vertices, config['outline'], config['width'])
        else:
            # Hanya outline menggunakan Bresenham
            self._render_bresenham_outline(vertices, config['outline'], config['width'])

        # ── Render overlay bantu ──────────────────────────────────────
        self._draw_centroid(shape)
        self._draw_shape_info(shape)

    def _bresenham_points(self, x0: int, y0: int, x1: int, y1: int) -> list:
        """Menghasilkan titik-titik garis menggunakan Bresenham Line Algorithm."""
        points = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            points.append((x0, y0))
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
        return points

    def _render_bresenham_outline(self, vertices: list, color: str, width: int):
        """Render garis tepi polygon menggunakan Bresenham."""
        if not color: return
        n = len(vertices)
        all_points = []
        for i in range(n):
            p1 = vertices[i]
            p2 = vertices[(i + 1) % n]
            x0, y0 = int(round(p1[0])), int(round(p1[1]))
            x1, y1 = int(round(p2[0])), int(round(p2[1]))
            all_points.extend(self._bresenham_points(x0, y0, x1, y1))
        
        # Plot pixel ke canvas
        r = width / 2.0
        for (x, y) in all_points:
            if width <= 1:
                # Plot 1 pixel
                self.canvas.create_rectangle(x, y, x, y, outline=color, tags=self._shape_tag)
            else:
                # Plot pixel tebal sebagai lingkaran kecil
                self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="", tags=self._shape_tag)

    def _render_scanline_fill(self, vertices: list, color: str):
        """Mengisi area polygon menggunakan Scanline Fill Algorithm."""
        if not color or len(vertices) < 3: return

        # 1. Kumpulkan semua edges (non-horizontal)
        edges = []
        n = len(vertices)
        for i in range(n):
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i + 1) % n]
            if y1 != y2:  # Abaikan garis horizontal murni
                if y1 > y2:
                    # Pastikan y1 adalah y minimum (titik atas)
                    x1, y1, x2, y2 = x2, y2, x1, y1
                # m_inv = 1 / m = dx / dy
                m_inv = (x2 - x1) / (y2 - y1)
                edges.append({'ymin': y1, 'ymax': y2, 'x': x1, 'm_inv': m_inv})

        if not edges: return

        # 2. Cari batas scanline
        min_y = int(math.floor(min(e['ymin'] for e in edges)))
        max_y = int(math.ceil(max(e['ymax'] for e in edges)))

        # 3. Proses scanline dari atas ke bawah
        for y in range(min_y, max_y + 1):
            intersections = []
            for e in edges:
                if e['ymin'] <= y < e['ymax']:
                    # Titik potong x pada scanline y
                    x_int = e['x'] + (y - e['ymin']) * e['m_inv']
                    intersections.append(x_int)
            
            # Sort titik potong dari kiri ke kanan
            intersections.sort()
            
            # Pasangkan titik potong untuk diisi warna
            for i in range(0, len(intersections) - 1, 2):
                x_start = int(round(intersections[i]))
                x_end = int(round(intersections[i + 1]))
                # Render horizontal line untuk mengisi fill area
                self.canvas.create_line(x_start, y, x_end, y, fill=color, tags=self._shape_tag)

    def clear(self):
        """Hapus semua elemen shape dan overlay dari canvas."""
        self.canvas.delete(self._shape_tag)
        self.canvas.delete(self._overlay_tag)
        # Gambar ulang placeholder teks
        self.canvas.create_text(
            self.cx, self.cy,
            text="Pilih objek untuk memulai",
            fill="#ADB5BD",
            font=("Consolas", 13),
            tags=self._overlay_tag,
        )

    # ─────────────────────────────────────────────────────────────────
    # ELEMEN BANTU
    # ─────────────────────────────────────────────────────────────────

    def _draw_background(self):
        """Gambar elemen latar tetap: garis sumbu bantu di tengah canvas."""
        # Garis horizontal tengah (sumbu X semu)
        self.canvas.create_line(
            0, self.cy, self.width, self.cy,
            fill=AXIS_COLOR, dash=AXIS_DASH, width=1,
            tags="background",
        )
        # Garis vertikal tengah (sumbu Y semu)
        self.canvas.create_line(
            self.cx, 0, self.cx, self.height,
            fill=AXIS_COLOR, dash=AXIS_DASH, width=1,
            tags="background",
        )
        # Label sumbu
        self.canvas.create_text(
            self.width - 8, self.cy - 8,
            text="X", fill=AXIS_COLOR, font=("Consolas", 9),
            tags="background",
        )
        self.canvas.create_text(
            self.cx + 8, 10,
            text="Y", fill=AXIS_COLOR, font=("Consolas", 9),
            tags="background",
        )
        # Titik origin (tengah canvas)
        self.canvas.create_oval(
            self.cx - 3, self.cy - 3,
            self.cx + 3, self.cy + 3,
            fill=AXIS_COLOR, outline="", tags="background",
        )
        self.canvas.create_text(
            self.cx + 10, self.cy + 10,
            text="O", fill=AXIS_COLOR, font=("Consolas", 8),
            tags="background",
        )

    def _draw_centroid(self, shape: BaseShape):
        """
        Gambar marker titik centroid objek saat ini.
        Menunjukkan pivot point untuk rotasi dan scaling.
        """
        cx, cy = shape.get_current_centroid()

        # Lingkaran kecil di centroid
        r = CENTROID_RADIUS
        self.canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            fill=CENTROID_COLOR,
            outline="#FFFFFF",
            width=1,
            tags=self._overlay_tag,
        )
        # Label centroid
        self.canvas.create_text(
            cx + 10, cy - 10,
            text=f"({cx:.0f}, {cy:.0f})",
            fill=CENTROID_COLOR,
            font=INFO_FONT,
            anchor="w",
            tags=self._overlay_tag,
        )

    def _draw_shape_info(self, shape: BaseShape):
        """Tampilkan nama objek dan ringkasan state transformasi di sudut canvas."""
        summary = shape.transform_state.get_summary()

        # Nama objek
        self.canvas.create_text(
            10, 10,
            text=f"● {shape.get_shape_name()}",
            fill=LABEL_COLOR,
            font=LABEL_FONT,
            anchor="nw",
            tags=self._overlay_tag,
        )

        # Info transformasi (kompak)
        tx, ty = summary['translasi']
        sx, sy = summary['skala']
        info_lines = [
            f"Translasi : ({tx:+.1f}, {ty:+.1f})",
            f"Rotasi    : {summary['rotasi']:.1f}°",
            f"Skala     : ({sx:.2f}, {sy:.2f})",
        ]
        if summary['refleksi_x'] or summary['refleksi_y']:
            rf = []
            if summary['refleksi_x']: rf.append("X")
            if summary['refleksi_y']: rf.append("Y")
            info_lines.append(f"Refleksi  : sumbu {', '.join(rf)}")
        shx, shy = summary['shear']
        if abs(shx) > 0.001 or abs(shy) > 0.001:
            info_lines.append(f"Shear     : ({shx:.2f}, {shy:.2f})")

        for i, line in enumerate(info_lines):
            self.canvas.create_text(
                10, 32 + i * 16,
                text=line,
                fill=INFO_COLOR,
                font=INFO_FONT,
                anchor="nw",
                tags=self._overlay_tag,
            )

    # ─────────────────────────────────────────────────────────────────
    # GETTER
    # ─────────────────────────────────────────────────────────────────

    def get_canvas_center(self) -> tuple:
        """Kembalikan koordinat (cx, cy) tengah canvas."""
        return (self.cx, self.cy)

    def get_canvas_size(self) -> tuple:
        """Kembalikan ukuran (width, height) canvas."""
        return (self.width, self.height)
