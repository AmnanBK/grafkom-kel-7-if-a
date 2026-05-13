"""
main.py
=======
Entry point aplikasi Grafika Komputer 2D.

Cara menjalankan:
    python main.py

Requirements:
    - Python 3.8+
    - tkinter  (sudah termasuk dalam instalasi Python standar)
    - numpy    (pip install numpy)

Mata Kuliah : Grafika Komputer
Semester    : Genap 2024/2025
Dosen       : Herry Sofyan, S.T., M.Kom.
"""

import tkinter as tk
import sys
import os

# Pastikan direktori project ada di path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import App


def main():
    """Inisialisasi Tkinter root window dan jalankan aplikasi."""
    root = tk.Tk()

    # Konfigurasi ikon (opsional — jika ada file icon.ico)
    try:
        # root.iconbitmap("icon.ico")
        pass
    except Exception:
        pass

    # Buat dan jalankan aplikasi
    application = App(root)

    # Mulai event loop Tkinter
    root.mainloop()


if __name__ == "__main__":
    main()
