# Aplikasi Grafika Komputer 2D - Kelompok 7 IF-A
**Proyek Tugas Besar Mata Kuliah Grafika Komputer — Semester Genap 2024/2025**
Dosen Pengampu: **Herry Sofyan, S.T., M.Kom.**

---

## Deskripsi Proyek
Aplikasi ini adalah perangkat lunak grafika komputer 2D interaktif yang dibangun menggunakan Python dan Tkinter. Fokus utama aplikasi ini adalah mendemonstrasikan implementasi algoritma grafika komputer dasar seperti **Rasterisasi Manual (Bresenham & Scanline Fill)** dan **Transformasi Geometri 2D** menggunakan matriks homogen 3x3.

### Fitur Utama:
- **Objek Primitif**: Mendukung pembuatan Persegi Panjang, Persegi, Segitiga, Lingkaran, dan Elips.
- **Rendering Manual**: 
  - Garis tepi menggunakan **Algoritma Bresenham**.
  - Pengisian warna menggunakan **Algoritma Scanline Fill**.
- **Transformasi Geometri 2D**:
  - **Translasi**: Pergeseran posisi (tx, ty).
  - **Rotasi**: Pemutaran objek terhadap titik pusat (centroid).
  - **Scaling**: Perubahan ukuran objek (sx, sy).
  - **Refleksi**: Pencerminan terhadap sumbu X dan Y.
  - **Shear**: Kemiringan objek pada sumbu X dan Y.
- **Transformasi Kumulatif**: Memungkinkan kombinasi beberapa transformasi sekaligus tanpa merusak bentuk dasar.
- **UI Modern**: Antarmuka pengguna dengan tema terang (*Light Mode*) yang bersih dan intuitif.

---

## Cara Menjalankan

### Prasyarat
- Python 3.8 ke atas
- NumPy (`pip install numpy`)

### Instalasi & Eksekusi
```bash
# 1. Clone repositori ini
git clone git@github.com:AmnanBK/grafkom-kel-7-if-a.git
cd grafkom-kel-7-if-a

# 2. Jalankan aplikasi
python main.py
```

---

## Struktur Proyek
```text
.
├── main.py                    # Entry point aplikasi
├── app.py                     # Controller utama (logika aplikasi)
├── shapes/                    # Modul pendefinisian objek geometris
│   ├── base_shape.py          # Abstract base class untuk semua shape
│   ├── rectangle.py           # Implementasi Persegi & Persegi Panjang
│   └── shapes.py              # Implementasi Segitiga, Lingkaran, & Elips
├── transform/                 # Modul logika matematika
│   ├── matrix2d.py            # Konstruksi matriks transformasi 3x3
│   └── transform_state.py     # Pengelolaan state transformasi kumulatif
└── ui/                        # Modul antarmuka pengguna
    ├── canvas_view.py         # Logika rendering manual (Bresenham & Scanline)
    └── control_panel.py       # Panel kontrol input & tombol
```

---

## Konsep Akademik yang Diimplementasikan

### 1. Koordinat Homogen
Setiap titik (vertex) dinyatakan dalam vektor `[x, y, 1]^T` untuk memungkinkan operasi translasi dilakukan melalui perkalian matriks.

### 2. Matriks Transformasi
Semua manipulasi objek menggunakan perkalian matriks 3x3:
- **Rotasi & Scaling**: Dilakukan terhadap titik pusat objek (*centroid*) menggunakan transformasi komposit: $M = T(x_c, y_c) \cdot R(\theta) \cdot T(-x_c, -y_c)$.

### 3. Rasterisasi Manual
Berbeda dengan aplikasi GUI standar yang menggunakan fungsi bawaan, aplikasi ini mengimplementasikan:
- **Bresenham Line Algorithm**: Untuk menggambar garis tepi (outline) pixel demi pixel.
- **Scanline Fill Algorithm**: Untuk mengisi area dalam poligon dengan memproses setiap baris scanline secara manual.

---

## Anggota Kelompok 7 (IF-A)
- [Nama Anggota 1]
- [Nama Anggota 2]
- [Nama Anggota 3]

---
*Dibuat untuk memenuhi persyaratan kelulusan mata kuliah Grafika Komputer 2025.*
