from django.urls import path
from . import views

urlpatterns = [
    # 1. Halaman Utama (Grafik Statistik Dashboard)
    path('', views.dashboard, name='main_dashboard'),
    
    # 2. Modul Buku
    path('buku/', views.daftar_buku_lama, name='dashboard'), # <-- Jalur ini sekarang aman karena fungsinya sudah ada di views.py
    path('buku/tambah/', views.tambah_buku, name='tambah_buku'),
    path('buku/<int:id_buku>/', views.detail_buku, name='detail_buku'),
    path('buku/edit/<int:id_buku>/', views.edit_buku, name='edit_buku'),
    path('buku/hapus/<int:id_buku>/', views.hapus_buku, name='hapus_buku'),

    # Modul User / Siswa
    path('siswa/', views.daftar_siswa, name='daftar_siswa'),
    path('siswa/tambah/', views.tambah_siswa, name='tambah_siswa'),
    path('siswa/<int:id_siswa>/', views.detail_siswa, name='detail_siswa'),
    path('siswa/edit/<int:id_siswa>/', views.edit_siswa, name='edit_siswa'),
    path('siswa/hapus/<int:id_siswa>/', views.hapus_siswa, name='hapus_siswa'),
    
    # Modul Peminjaman
    path('peminjaman/', views.daftar_peminjaman, name='daftar_peminjaman'),
    path('peminjaman/tambah/', views.tambah_peminjaman, name='tambah_peminjaman'),
    path('peminjaman/kembalikan/<int:id_peminjaman>/', views.kembalikan_buku, name='kembalikan_buku'),
    path('peminjaman/hapus/<int:id_peminjaman>/', views.hapus_peminjaman, name='hapus_peminjaman'),
]