# Aplikasi Grafika Komputer 2D
**Mata Kuliah Grafika Komputer — Semester Genap 2024/2025**
Dosen: Herry Sofyan, S.T., M.Kom.

---

## Cara Menjalankan

```bash
# 1. Pastikan Python 3.8+ terinstall
python --version

# 2. Install NumPy jika belum ada
pip install numpy

# 3. Jalankan aplikasi
cd grafika2d
python main.py
```

> **Catatan**: Tkinter sudah termasuk dalam instalasi Python standar di Windows dan macOS. Di Linux, install dengan: `sudo apt install python3-tk`

---

## Struktur Proyek

```
grafika2d/
├── main.py                    ← Entry point
├── app.py                     ← Controller utama (MVC)
├── shapes/
│   ├── base_shape.py          ← Abstract class
│   ├── rectangle.py           ← Persegi Panjang & Persegi
│   └── shapes.py              ← Segitiga, Lingkaran, Elips
├── transform/
│   ├── matrix2d.py            ← Matriks transformasi 2D (INTI AKADEMIK)
│   └── transform_state.py     ← State kumulatif transformasi
└── ui/
    ├── canvas_view.py          ← Rendering ke Tkinter Canvas
    └── control_panel.py        ← Panel kontrol UI
```

---

## Konsep Grafika Komputer yang Diimplementasikan

### Koordinat Homogen
Setiap titik dinyatakan dalam vektor homogen `[x, y, 1]^T`.
Semua transformasi menggunakan matriks 3×3.

### Matriks Transformasi (dari materi dosen)

| Transformasi | Matriks 3×3 |
|---|---|
| Translasi | `[[1,0,tx],[0,1,ty],[0,0,1]]` |
| Scaling | `[[sx,0,0],[0,sy,0],[0,0,1]]` |
| Rotasi | `[[cosθ,-sinθ,0],[sinθ,cosθ,0],[0,0,1]]` |
| Refleksi X | `[[1,0,0],[0,-1,0],[0,0,1]]` |
| Refleksi Y | `[[-1,0,0],[0,1,0],[0,0,1]]` |
| Shear | `[[1,shx,0],[shy,1,0],[0,0,1]]` |

### Transformasi Komposit
Rotasi dan scaling terhadap pivot point menggunakan komposit:
```
M = T(xp,yp) · R(θ) · T(-xp,-yp)
```
Perkalian dari kanan ke kiri (sesuai materi dosen).

### Sistem Koordinat
Canvas Tkinter menggunakan koordinat layar (Y ke bawah).
Rotasi θ positif = searah jarum jam di canvas.
Hal ini harus dijelaskan dalam laporan BAB III.

---

## Fitur Transformasi

| Fitur | Status | Keterangan |
|---|---|---|
| Translasi | ✅ Wajib | Input tx, ty dalam pixel |
| Scaling | ✅ Wajib | Input sx, sy (misal: 1.5 = 150%) |
| Rotasi | ✅ Wajib | Input θ dalam derajat, pivot = centroid |
| Refleksi X/Y | ✅ Opsional | Tombol toggle |
| Shear | ✅ Opsional | Input shx, shy |

Semua transformasi bersifat **kumulatif**.

---

## Catatan untuk Laporan

### BAB I — Teori Dasar
Referensikan `transform/matrix2d.py` untuk penjelasan matriks.
Setiap fungsi dilengkapi docstring yang menjelaskan rumus dari materi dosen.

### BAB II — Perancangan Aplikasi
Gunakan struktur folder dan diagram class sebagai perancangan menu dan antar muka.

### BAB III — Implementasi Program
- **Perangkat keras**: Spesifikasi komputer yang digunakan
- **Perangkat lunak**: Python 3.x, Tkinter, NumPy
- **Tampilan**: Screenshot aplikasi
- **Modul**: Jelaskan fungsi setiap file `.py`

---

## Cara Presentasi

1. Buka aplikasi → pilih objek (misal: Segitiga)
2. Tunjukkan mode Fill vs Outline
3. Lakukan Translasi → jelaskan matriks di matrix2d.py
4. Lakukan Rotasi → tunjukkan centroid marker (titik merah)
5. Lakukan Scaling → tunjukkan objek membesar/mengecil
6. Lakukan Reset → tunjukkan objek kembali ke posisi asal
7. Tunjukkan kumulatif: rotasi 30° × 3 = 90° total
8. (Opsional) Tunjukkan Refleksi dan Shear
