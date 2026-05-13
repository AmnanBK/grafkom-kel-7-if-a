"""
rectangle.py
============
Implementasi primitif Persegi Panjang dan Persegi.

Persegi adalah special case dari Persegi Panjang dengan width == height.
Vertices digenerate searah jarum jam mulai dari pojok kiri-atas.
"""

from shapes.base_shape import BaseShape


class Rectangle(BaseShape):
    """
    Persegi panjang — 4 vertices di pojok-pojoknya.

    Vertices (searah jarum jam dari pojok kiri-atas):
        [0] top-left     : (cx - w/2, cy - h/2)
        [1] top-right    : (cx + w/2, cy - h/2)
        [2] bottom-right : (cx + w/2, cy + h/2)
        [3] bottom-left  : (cx - w/2, cy + h/2)
    """

    def __init__(
        self,
        canvas_cx: float,
        canvas_cy: float,
        width: float = 160,
        height: float = 100,
        **kwargs,
    ):
        """
        Args:
            canvas_cx: Koordinat X pusat canvas
            canvas_cy: Koordinat Y pusat canvas
            width: Lebar persegi panjang (pixel)
            height: Tinggi persegi panjang (pixel)
        """
        self.width  = width
        self.height = height
        super().__init__(canvas_cx, canvas_cy, **kwargs)

    def _generate_vertices(self, cx: float, cy: float) -> list:
        """Generate 4 vertices persegi panjang di sekitar titik (cx, cy)."""
        half_w = self.width  / 2
        half_h = self.height / 2
        return [
            (cx - half_w, cy - half_h),   # top-left
            (cx + half_w, cy - half_h),   # top-right
            (cx + half_w, cy + half_h),   # bottom-right
            (cx - half_w, cy + half_h),   # bottom-left
        ]

    def get_shape_name(self) -> str:
        return "Persegi Panjang"


class Square(Rectangle):
    """
    Persegi — persegi panjang dengan lebar == tinggi.
    Mewarisi semua perilaku Rectangle, cukup override ukuran.
    """

    def __init__(
        self,
        canvas_cx: float,
        canvas_cy: float,
        size: float = 110,
        **kwargs,
    ):
        """
        Args:
            canvas_cx: Koordinat X pusat canvas
            canvas_cy: Koordinat Y pusat canvas
            size: Panjang sisi persegi (pixel)
        """
        # Panggil Rectangle dengan width == height == size
        super().__init__(canvas_cx, canvas_cy, width=size, height=size, **kwargs)

    def get_shape_name(self) -> str:
        return "Persegi"
