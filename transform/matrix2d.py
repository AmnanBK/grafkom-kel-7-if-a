"""
matrix2d.py
===========
Fungsi-fungsi pembentuk matriks transformasi 2D menggunakan koordinat homogen.

Referensi materi dosen:
  - Setiap titik dinyatakan dalam koordinat homogen (x, y, 1)
  - Semua transformasi dinyatakan dalam matriks 3x3
  - Transformasi komposit diperoleh dengan perkalian matriks dari kanan ke kiri:
        M_komposit = Mn · ... · M2 · M1
  - Berlaku: P' = M · P

Sistem koordinat:
  - Tkinter Canvas: sumbu Y ke BAWAH (berbeda dari koordinat Cartesian matematis)
  - Rotasi positif (θ > 0) → searah jarum jam di canvas (konvensi layar)
  - Hal ini harus dijelaskan dalam laporan
"""

import numpy as np
import math


# ─────────────────────────────────────────────────
# 1. MATRIKS TRANSLASI
# ─────────────────────────────────────────────────

def translation_matrix(tx: float, ty: float) -> np.ndarray:
    """
    Matriks translasi 2D dalam koordinat homogen.

    Rumus (materi dosen):
        x' = x + tx
        y' = y + ty

    Matriks:
        | 1  0  tx |
        | 0  1  ty |
        | 0  0   1 |

    Args:
        tx: Faktor translasi pada sumbu X
        ty: Faktor translasi pada sumbu Y

    Returns:
        Matriks translasi 3x3 (numpy array)
    """
    return np.array([
        [1, 0, tx],
        [0, 1, ty],
        [0, 0,  1]
    ], dtype=float)


# ─────────────────────────────────────────────────
# 2. MATRIKS SCALING (SKALA)
# ─────────────────────────────────────────────────

def scaling_matrix(sx: float, sy: float) -> np.ndarray:
    """
    Matriks penskalaan 2D dalam koordinat homogen.

    Rumus (materi dosen):
        x' = sx * x
        y' = sy * y

    Matriks:
        | sx  0   0 |
        |  0  sy  0 |
        |  0   0  1 |

    Catatan:
        - sx, sy > 1  → objek diperbesar
        - 0 < sx, sy < 1 → objek diperkecil
        - sx == sy → uniform scaling

    Args:
        sx: Faktor skala pada sumbu X
        sy: Faktor skala pada sumbu Y

    Returns:
        Matriks scaling 3x3 (numpy array)
    """
    if sx == 0 or sy == 0:
        raise ValueError("Faktor skala tidak boleh nol.")
    return np.array([
        [sx,  0, 0],
        [ 0, sy, 0],
        [ 0,  0, 1]
    ], dtype=float)


# ─────────────────────────────────────────────────
# 3. MATRIKS ROTASI
# ─────────────────────────────────────────────────

def rotation_matrix(theta_deg: float) -> np.ndarray:
    """
    Matriks rotasi 2D terhadap titik pusat koordinat (0, 0).

    Penurunan rumus (materi dosen - dari koordinat polar):
        x  = r cos(Φ)
        y  = r sin(Φ)
        x' = r cos(Φ + θ) = x cos θ - y sin θ
        y' = r sin(Φ + θ) = x sin θ + y cos θ

    Matriks:
        | cos θ  -sin θ  0 |
        | sin θ   cos θ  0 |
        |   0       0    1 |

    Catatan sistem koordinat canvas:
        Karena sumbu Y canvas menghadap ke bawah, rotasi θ positif
        menghasilkan rotasi SEARAH jarum jam (berlawanan dengan konvensi
        matematika standar). Ini harus dijelaskan di laporan.

    Args:
        theta_deg: Sudut rotasi dalam derajat

    Returns:
        Matriks rotasi 3x3 (numpy array)
    """
    theta = math.radians(theta_deg)
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    return np.array([
        [cos_t, -sin_t, 0],
        [sin_t,  cos_t, 0],
        [    0,      0, 1]
    ], dtype=float)


# ─────────────────────────────────────────────────
# 4. ROTASI TERHADAP PIVOT POINT (KOMPOSIT)
# ─────────────────────────────────────────────────

def rotation_around_pivot(theta_deg: float, xp: float, yp: float) -> np.ndarray:
    """
    Rotasi terhadap titik pivot (xp, yp) menggunakan transformasi komposit.

    Prosedur (materi dosen, hal. Transformasi Komposit):
        1. Translasikan objek sehingga pivot point berada di origin (0,0):
               T1 = T(-xp, -yp)
        2. Rotasi terhadap origin:
               R  = R(θ)
        3. Translasikan kembali ke posisi semula:
               T2 = T(xp, yp)

    Matriks komposit (kanan ke kiri):
        M = T2 · R · T1

    Args:
        theta_deg: Sudut rotasi dalam derajat
        xp: Koordinat X pivot point
        yp: Koordinat Y pivot point

    Returns:
        Matriks rotasi komposit 3x3 (numpy array)
    """
    T1 = translation_matrix(-xp, -yp)
    R  = rotation_matrix(theta_deg)
    T2 = translation_matrix(xp, yp)
    # Perkalian dari kanan ke kiri: T2 · R · T1
    return T2 @ R @ T1


# ─────────────────────────────────────────────────
# 5. SCALING TERHADAP FIXED POINT (KOMPOSIT)
# ─────────────────────────────────────────────────

def scaling_around_pivot(sx: float, sy: float, xf: float, yf: float) -> np.ndarray:
    """
    Penskalaan terhadap fixed point (xf, yf) menggunakan transformasi komposit.

    Rumus (materi dosen):
        x' = xf + (x - xf) * sx
        y' = yf + (y - yf) * sy

    Prosedur komposit:
        1. T(-xf, -yf) → pindahkan fixed point ke origin
        2. S(sx, sy)   → scaling
        3. T(xf, yf)   → kembalikan ke posisi semula

    Args:
        sx: Faktor skala sumbu X
        sy: Faktor skala sumbu Y
        xf: Koordinat X fixed point (centroid)
        yf: Koordinat Y fixed point (centroid)

    Returns:
        Matriks scaling komposit 3x3 (numpy array)
    """
    T1 = translation_matrix(-xf, -yf)
    S  = scaling_matrix(sx, sy)
    T2 = translation_matrix(xf, yf)
    return T2 @ S @ T1


# ─────────────────────────────────────────────────
# 6. REFLEKSI (OPSIONAL)
# ─────────────────────────────────────────────────

def reflection_matrix(axis: str) -> np.ndarray:
    """
    Matriks refleksi terhadap sumbu X atau Y.

    Refleksi terhadap sumbu X (y menjadi -y):
        |  1   0  0 |
        |  0  -1  0 |
        |  0   0  1 |

    Refleksi terhadap sumbu Y (x menjadi -x):
        | -1   0  0 |
        |  0   1  0 |
        |  0   0  1 |

    Args:
        axis: 'x' untuk refleksi terhadap sumbu X,
              'y' untuk refleksi terhadap sumbu Y

    Returns:
        Matriks refleksi 3x3 (numpy array)
    """
    if axis.lower() == 'x':
        return np.array([
            [ 1,  0, 0],
            [ 0, -1, 0],
            [ 0,  0, 1]
        ], dtype=float)
    elif axis.lower() == 'y':
        return np.array([
            [-1,  0, 0],
            [ 0,  1, 0],
            [ 0,  0, 1]
        ], dtype=float)
    else:
        raise ValueError("Axis harus 'x' atau 'y'.")


def reflection_around_pivot(axis: str, xp: float, yp: float) -> np.ndarray:
    """
    Refleksi terhadap sumbu yang melewati pivot point (xp, yp).

    Prosedur komposit:
        1. T(-xp, -yp)   → pindahkan pivot ke origin
        2. Reflect(axis) → refleksi
        3. T(xp, yp)     → kembalikan

    Args:
        axis: 'x' atau 'y'
        xp, yp: Koordinat pivot point

    Returns:
        Matriks refleksi komposit 3x3
    """
    T1 = translation_matrix(-xp, -yp)
    RF = reflection_matrix(axis)
    T2 = translation_matrix(xp, yp)
    return T2 @ RF @ T1


# ─────────────────────────────────────────────────
# 7. SHEAR (OPSIONAL)
# ─────────────────────────────────────────────────

def shear_matrix(shx: float = 0.0, shy: float = 0.0) -> np.ndarray:
    """
    Matriks shear (geser) 2D.

    Shear pada sumbu X (shx):
        x' = x + shx * y
        y' = y

    Shear pada sumbu Y (shy):
        x' = x
        y' = y + shy * x

    Matriks:
        |  1   shx  0 |
        |  shy  1   0 |
        |  0    0   1 |

    Args:
        shx: Faktor shear pada sumbu X (default 0)
        shy: Faktor shear pada sumbu Y (default 0)

    Returns:
        Matriks shear 3x3 (numpy array)
    """
    return np.array([
        [  1, shx, 0],
        [shy,   1, 0],
        [  0,   0, 1]
    ], dtype=float)


# ─────────────────────────────────────────────────
# 8. FUNGSI UTILITAS: TERAPKAN MATRIKS KE VERTICES
# ─────────────────────────────────────────────────

def apply_transform(matrix: np.ndarray, vertices: list) -> list:
    """
    Terapkan matriks transformasi 3x3 ke semua titik (vertices).

    Setiap titik (x, y) diubah menjadi vektor homogen [x, y, 1],
    dikalikan dengan matriks transformasi, lalu dikembalikan ke (x', y').

    Rumus: P' = M · P
    dimana P = [x, y, 1]^T (vektor kolom koordinat homogen)

    Args:
        matrix: Matriks transformasi 3x3 (numpy array)
        vertices: List of (x, y) tuples

    Returns:
        List of (x', y') tuples hasil transformasi
    """
    result = []
    for (x, y) in vertices:
        # Konversi ke koordinat homogen: [x, y, 1]
        p_homogen = np.array([x, y, 1.0])
        # Terapkan transformasi: P' = M · P
        p_transformed = matrix @ p_homogen
        # Ambil koordinat Cartesian: (x', y') dari (xh, yh, h)
        result.append((p_transformed[0], p_transformed[1]))
    return result


def compute_centroid(vertices: list) -> tuple:
    """
    Hitung centroid (titik tengah) dari kumpulan vertices.

    Centroid = rata-rata koordinat semua titik.
    Digunakan sebagai pivot point default untuk rotasi dan scaling.

    Args:
        vertices: List of (x, y) tuples

    Returns:
        Tuple (cx, cy) koordinat centroid
    """
    if not vertices:
        return (0.0, 0.0)
    cx = sum(v[0] for v in vertices) / len(vertices)
    cy = sum(v[1] for v in vertices) / len(vertices)
    return (cx, cy)
