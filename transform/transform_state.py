"""
transform_state.py
==================
Manajemen state transformasi kumulatif untuk satu objek aktif.

Pendekatan dua-lapis:
  - original_vertices  : titik-titik ASLI objek, tidak pernah diubah
  - TransformState     : akumulasi semua transformasi yang sudah diterapkan
  - current_vertices   : dihitung ulang dari original + transform_state setiap kali

Keuntungan pendekatan ini:
  - Menghindari akumulasi floating point error
  - Rotasi & scaling selalu dari centroid ASLI (bukan centroid yang sudah bergeser)
  - Reset hanya perlu me-reset TransformState ke nilai default
  - Pipeline transformasi tetap konsisten dan mudah di-debug
"""

from transform.matrix2d import (
    translation_matrix,
    rotation_around_pivot,
    scaling_around_pivot,
    reflection_around_pivot,
    shear_matrix,
    apply_transform,
    compute_centroid
)
import numpy as np


class TransformState:
    """
    Menyimpan akumulasi semua transformasi yang telah diterapkan ke sebuah objek.

    State ini bersifat KUMULATIF:
        - tx, ty  : total translasi dari posisi asal
        - angle   : total sudut rotasi (derajat)
        - sx, sy  : faktor skala kumulatif (perkalian)

    Pipeline komputasi current_vertices:
        M = T(tx,ty) · T(cx,cy) · R(angle) · S(sx,sy) · T(-cx,-cy)
        current_vertices = apply_transform(M, original_vertices)

    Urutan transformasi (kanan ke kiri):
        1. Pindahkan centroid ke origin       : T(-cx, -cy)
        2. Scale dari origin                  : S(sx, sy)
        3. Rotate dari origin                 : R(angle)
        4. Kembalikan centroid ke posisi asal : T(cx, cy)
        5. Terapkan translasi kumulatif       : T(tx, ty)
    """

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset semua transformasi ke keadaan awal (identitas)."""
        self.tx    = 0.0   # translasi kumulatif sumbu X
        self.ty    = 0.0   # translasi kumulatif sumbu Y
        self.angle = 0.0   # rotasi kumulatif dalam derajat
        self.sx    = 1.0   # faktor skala kumulatif sumbu X
        self.sy    = 1.0   # faktor skala kumulatif sumbu Y
        # Transformasi opsional (refleksi & shear)
        self.reflect_x = False  # apakah sudah direfleksi terhadap sumbu X
        self.reflect_y = False  # apakah sudah direfleksi terhadap sumbu Y
        self.shx   = 0.0   # shear pada sumbu X
        self.shy   = 0.0   # shear pada sumbu Y

    def apply_translation(self, tx: float, ty: float):
        """Tambahkan translasi kumulatif."""
        self.tx += tx
        self.ty += ty

    def apply_rotation(self, delta_angle: float):
        """Tambahkan rotasi kumulatif (dalam derajat)."""
        self.angle += delta_angle
        # Normalisasi agar sudut tetap dalam range [0, 360)
        self.angle = self.angle % 360

    def apply_scaling(self, sx: float, sy: float):
        """Kalikan faktor skala kumulatif."""
        if sx <= 0 or sy <= 0:
            raise ValueError("Faktor skala harus positif (> 0).")
        self.sx *= sx
        self.sy *= sy

    def apply_reflection_x(self):
        """Toggle refleksi terhadap sumbu X."""
        self.reflect_x = not self.reflect_x

    def apply_reflection_y(self):
        """Toggle refleksi terhadap sumbu Y."""
        self.reflect_y = not self.reflect_y

    def apply_shear(self, shx: float, shy: float):
        """Tambahkan shear kumulatif."""
        self.shx += shx
        self.shy += shy

    def compute(self, original_vertices: list) -> list:
        """
        Hitung current_vertices dari original_vertices + state transformasi saat ini.

        Pipeline matriks (kanan ke kiri sesuai materi dosen):
            M = T(tx,ty) · SH · RF · T(cx,cy) · R(angle) · S(sx,sy) · T(-cx,-cy)

        Args:
            original_vertices: List of (x, y) titik-titik asli objek

        Returns:
            List of (x', y') titik-titik setelah transformasi
        """
        if not original_vertices:
            return []

        # Hitung centroid dari vertices ASLI sebagai pivot point
        cx, cy = compute_centroid(original_vertices)

        # ── Langkah 1: Bangun matriks transformasi ──────────────────────────

        # Pindahkan centroid ke origin
        T_neg = translation_matrix(-cx, -cy)

        # Scaling dari origin
        S = scaling_around_pivot(self.sx, self.sy, 0, 0)

        # Rotasi dari origin
        R = rotation_around_pivot(self.angle, 0, 0)

        # Kembalikan centroid ke posisi asal
        T_pos = translation_matrix(cx, cy)

        # Translasi kumulatif
        T_trans = translation_matrix(self.tx, self.ty)

        # Shear (jika ada)
        SH = shear_matrix(self.shx, self.shy)

        # ── Langkah 2: Matriks komposit (kanan ke kiri) ─────────────────────
        # Urutan: pindah ke origin → scale → rotate → balik → shear → translasi

        # Transformasi dasar dari centroid: T_pos · R · S · T_neg
        M_core = T_pos @ R @ S @ T_neg

        # Tambahkan shear
        M_with_shear = SH @ M_core

        # Tambahkan translasi kumulatif
        M_final = T_trans @ M_with_shear

        # ── Langkah 3: Terapkan refleksi ─────────────────────────────────────
        # Refleksi dilakukan terhadap centroid objek saat ini (setelah translasi)
        # Hitung posisi centroid setelah translasi
        vertices_after_core = apply_transform(M_final, original_vertices)
        cx_curr, cy_curr = compute_centroid(vertices_after_core)

        if self.reflect_x:
            RF_x = reflection_around_pivot('x', cx_curr, cy_curr)
            vertices_after_core = apply_transform(RF_x, vertices_after_core)

        if self.reflect_y:
            RF_y = reflection_around_pivot('y', cx_curr, cy_curr)
            vertices_after_core = apply_transform(RF_y, vertices_after_core)

        return vertices_after_core

    def get_summary(self) -> dict:
        """
        Ringkasan state transformasi saat ini.
        Berguna untuk ditampilkan di panel informasi UI.

        Returns:
            Dictionary berisi nilai semua transformasi aktif
        """
        return {
            'translasi': (self.tx, self.ty),
            'rotasi': self.angle,
            'skala': (self.sx, self.sy),
            'refleksi_x': self.reflect_x,
            'refleksi_y': self.reflect_y,
            'shear': (self.shx, self.shy),
        }
