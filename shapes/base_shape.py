"""
base_shape.py
=============
Abstract base class untuk semua primitif geometri.

Setiap shape menyimpan:
  - original_vertices : titik-titik asli (tidak pernah berubah)
  - transform_state   : akumulasi transformasi
  - fill_mode         : True = fill penuh, False = outline saja
  - color             : warna objek
  - outline_color     : warna garis tepi (untuk mode fill)
  - outline_width     : ketebalan garis

Subclass wajib mengimplementasikan:
  - _generate_vertices(cx, cy) → list[(x,y)]
"""

from abc import ABC, abstractmethod
from transform.transform_state import TransformState


class BaseShape(ABC):
    """
    Abstract base class untuk semua primitif grafika 2D.

    Attributes:
        original_vertices (list): Titik-titik asli objek di posisi awal
        transform_state (TransformState): Akumulasi transformasi kumulatif
        fill_mode (bool): True = filled, False = outline only
        color (str): Warna fill objek
        outline_color (str): Warna garis tepi
        outline_width (int): Ketebalan garis tepi (pixel)
    """

    # Ukuran default objek di canvas (dalam pixel)
    DEFAULT_SIZE = 100

    def __init__(
        self,
        canvas_cx: float,
        canvas_cy: float,
        fill_mode: bool = True,
        fill_color: str = "#4A90D9",
        outline_color: str = "#1A3A5C",
        outline_width: int = 2,
    ):
        """
        Inisialisasi shape di tengah canvas.

        Args:
            canvas_cx: Koordinat X tengah canvas (tempat objek muncul)
            canvas_cy: Koordinat Y tengah canvas
            fill_mode: True untuk fill, False untuk outline saja
            color: Warna fill (hex string atau nama warna Tkinter)
            outline_color: Warna garis tepi
            outline_width: Ketebalan garis tepi
        """
        self.fill_mode    = fill_mode
        self.fill_color        = fill_color
        self.outline_color = outline_color
        self.outline_width = outline_width
        self.transform_state = TransformState()

        # Generate titik-titik asli di posisi tengah canvas
        self.original_vertices = self._generate_vertices(canvas_cx, canvas_cy)

    @abstractmethod
    def _generate_vertices(self, cx: float, cy: float) -> list:
        """
        Generate titik-titik (vertices) asli dari objek.

        Dipanggil sekali saat inisialisasi. Hasilnya disimpan di
        original_vertices dan TIDAK PERNAH diubah setelahnya.

        Args:
            cx: Koordinat X pusat objek
            cy: Koordinat Y pusat objek

        Returns:
            List of (x, y) tuples, searah jarum jam
        """
        pass

    @abstractmethod
    def get_shape_name(self) -> str:
        """Nama objek untuk ditampilkan di UI."""
        pass

    def get_current_vertices(self) -> list:
        """
        Hitung dan kembalikan posisi vertices saat ini.

        Selalu dihitung ulang dari original_vertices + transform_state,
        TIDAK disimpan sebagai state (menghindari floating point drift).

        Returns:
            List of (x', y') tuples setelah semua transformasi
        """
        return self.transform_state.compute(self.original_vertices)

    def get_centroid(self) -> tuple:
        """
        Hitung centroid dari original_vertices.

        Digunakan sebagai pivot point default untuk rotasi dan scaling.
        Menggunakan original_vertices agar pivot selalu konsisten.

        Returns:
            Tuple (cx, cy)
        """
        vertices = self.original_vertices
        if not vertices:
            return (0.0, 0.0)
        cx = sum(v[0] for v in vertices) / len(vertices)
        cy = sum(v[1] for v in vertices) / len(vertices)
        return (cx, cy)

    def get_current_centroid(self) -> tuple:
        """
        Hitung centroid dari current_vertices (posisi setelah transformasi).

        Berguna untuk menampilkan info posisi aktual di UI.

        Returns:
            Tuple (cx, cy) centroid saat ini
        """
        vertices = self.get_current_vertices()
        if not vertices:
            return (0.0, 0.0)
        cx = sum(v[0] for v in vertices) / len(vertices)
        cy = sum(v[1] for v in vertices) / len(vertices)
        return (cx, cy)

    def reset(self):
        """
        Reset semua transformasi ke posisi asal.

        Cukup reset TransformState — original_vertices tidak berubah.
        """
        self.transform_state.reset()

    def set_fill_mode(self, fill_mode: bool):
        """Ubah mode render: True = fill, False = outline."""
        self.fill_mode = fill_mode

    def set_fill_color(self, fill_color: str):
        """Ubah warna fill objek."""
        self.fill_color = fill_color

    def set_outline_color(self, color: str):
        """Ubah warna garis tepi."""
        self.outline_color = color

    def get_render_config(self) -> dict:
        """
        Kembalikan konfigurasi rendering untuk CanvasView.

        Returns:
            Dictionary berisi:
                - vertices: list (x, y) saat ini
                - fill: warna fill ('' jika outline mode)
                - outline: warna garis tepi
                - width: ketebalan garis
        """
        return {
            'vertices'      : self.get_current_vertices(),
            'fill'          : self.fill_color if self.fill_mode else '',
            'outline'       : self.outline_color,
            'width'         : self.outline_width,
            'fill_mode'     : self.fill_mode,
        }
