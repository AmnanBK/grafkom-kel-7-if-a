"""
triangle.py / circle.py / ellipse.py — dalam satu file untuk kemudahan
=======================================================================
Implementasi primitif: Segitiga, Lingkaran, dan Elips.

Lingkaran dan Elips diimplementasikan sebagai N-polygon (poligon dengan
banyak titik) agar transformasi matriks bisa diterapkan langsung ke vertices,
sesuai pendekatan grafika komputer dari materi dosen.

N = 72 (setiap 5 derajat) memberikan approximasi yang sangat halus.
"""

import math
from shapes.base_shape import BaseShape


# ─────────────────────────────────────────────────────────────────────
# SEGITIGA
# ─────────────────────────────────────────────────────────────────────

class Triangle(BaseShape):
    """
    Segitiga sama kaki dengan puncak di atas.

    Vertices (searah jarum jam):
        [0] atas   : (cx, cy - h*2/3)        ← puncak
        [1] kanan  : (cx + w/2, cy + h/3)    ← kaki kanan
        [2] kiri   : (cx - w/2, cy + h/3)    ← kaki kiri

    Pemilihan proporsi 2/3 dan 1/3 dari tinggi menjadikan centroid
    geometri berada tepat di (cx, cy).
    """

    def __init__(
        self,
        canvas_cx: float,
        canvas_cy: float,
        base: float = 140,
        height: float = 120,
        **kwargs,
    ):
        """
        Args:
            canvas_cx: Koordinat X pusat canvas
            canvas_cy: Koordinat Y pusat canvas
            base: Lebar alas segitiga (pixel)
            height: Tinggi segitiga (pixel)
        """
        self.base   = base
        self.tri_height = height
        super().__init__(canvas_cx, canvas_cy, **kwargs)

    def _generate_vertices(self, cx: float, cy: float) -> list:
        """
        Generate 3 vertices segitiga sama kaki.
        Centroid segitiga berada pada 1/3 tinggi dari alas,
        atau 2/3 tinggi dari puncak.
        """
        half_base = self.base / 2
        # Dengan pembagian 2/3 dan 1/3, centroid tepat di (cx, cy)
        top    = (cx,               cy - self.tri_height * 2 / 3)
        right  = (cx + half_base,   cy + self.tri_height / 3)
        left   = (cx - half_base,   cy + self.tri_height / 3)
        return [top, right, left]

    def get_shape_name(self) -> str:
        return "Segitiga"


# ─────────────────────────────────────────────────────────────────────
# LINGKARAN
# ─────────────────────────────────────────────────────────────────────

class Circle(BaseShape):
    """
    Lingkaran — direpresentasikan sebagai N-gon beraturan.

    Mengapa N-gon bukan arc bawaan Tkinter?
    → Agar transformasi matriks bisa diterapkan langsung ke setiap vertex,
      sesuai konsep grafika komputer dari materi dosen (transformasi bekerja
      pada kumpulan titik, bukan pada parameter geometri seperti radius).

    Vertices digenerate dengan:
        x_i = cx + r * cos(2π * i / N)
        y_i = cy + r * sin(2π * i / N)

    N = 72 → satu titik setiap 5° → tampak sangat mulus.
    """

    N_SEGMENTS = 72  # Jumlah segmen (semakin besar semakin mulus)

    def __init__(
        self,
        canvas_cx: float,
        canvas_cy: float,
        radius: float = 70,
        **kwargs,
    ):
        """
        Args:
            canvas_cx: Koordinat X pusat canvas
            canvas_cy: Koordinat Y pusat canvas
            radius: Jari-jari lingkaran (pixel)
        """
        self.radius = radius
        super().__init__(canvas_cx, canvas_cy, **kwargs)

    def _generate_vertices(self, cx: float, cy: float) -> list:
        """
        Generate N titik di sekeliling lingkaran menggunakan fungsi trigonometri.

        Persamaan parametrik lingkaran:
            x = cx + r * cos(θ)
            y = cy + r * sin(θ)
        dimana θ dari 0 hingga 2π.
        """
        vertices = []
        for i in range(self.N_SEGMENTS):
            theta = 2 * math.pi * i / self.N_SEGMENTS
            x = cx + self.radius * math.cos(theta)
            y = cy + self.radius * math.sin(theta)
            vertices.append((x, y))
        return vertices

    def get_shape_name(self) -> str:
        return "Lingkaran"


# ─────────────────────────────────────────────────────────────────────
# ELIPS
# ─────────────────────────────────────────────────────────────────────

class Ellipse(BaseShape):
    """
    Elips — direpresentasikan sebagai N-gon eliptis.

    Sama seperti Lingkaran, diimplementasikan sebagai poligon agar
    transformasi matriks dapat diterapkan ke semua titik.

    Vertices digenerate dengan:
        x_i = cx + rx * cos(2π * i / N)
        y_i = cy + ry * sin(2π * i / N)

    dimana rx = radius horizontal, ry = radius vertikal.
    Jika rx == ry → menjadi lingkaran.
    """

    N_SEGMENTS = 72

    def __init__(
        self,
        canvas_cx: float,
        canvas_cy: float,
        radius_x: float = 110,
        radius_y: float = 65,
        **kwargs,
    ):
        """
        Args:
            canvas_cx: Koordinat X pusat canvas
            canvas_cy: Koordinat Y pusat canvas
            radius_x: Jari-jari horizontal / semi-major axis (pixel)
            radius_y: Jari-jari vertikal / semi-minor axis (pixel)
        """
        self.radius_x = radius_x
        self.radius_y = radius_y
        super().__init__(canvas_cx, canvas_cy, **kwargs)

    def _generate_vertices(self, cx: float, cy: float) -> list:
        """
        Generate N titik di sekeliling elips menggunakan persamaan parametrik.

        Persamaan parametrik elips:
            x = cx + rx * cos(θ)
            y = cy + ry * sin(θ)
        """
        vertices = []
        for i in range(self.N_SEGMENTS):
            theta = 2 * math.pi * i / self.N_SEGMENTS
            x = cx + self.radius_x * math.cos(theta)
            y = cy + self.radius_y * math.sin(theta)
            vertices.append((x, y))
        return vertices

    def get_shape_name(self) -> str:
        return "Elips"
