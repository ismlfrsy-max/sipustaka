from django.shortcuts import render, redirect
from django.db import connection 
from datetime import datetime, timedelta# <-- Ini penting untuk menjalankan Raw SQL

def dashboard(request):
    with connection.cursor() as cursor:
        # 1. Total Buku (Menghitung SUM dari kolom 'stok' di tabel buku)
        cursor.execute("SELECT COALESCE(SUM(stok), 0) FROM buku")
        total_buku = cursor.fetchone()[0]

        # 2. Total Judul (Menghitung total baris/koleksi judul unik di tabel buku)
        cursor.execute("SELECT COUNT(*) FROM buku")
        total_judul = cursor.fetchone()[0]

        # 3. Sedang Dipinjam (Status 'Dipinjam')
        cursor.execute("SELECT COUNT(*) FROM peminjaman WHERE status = 'Dipinjam'")
        sedang_dipinjam = cursor.fetchone()[0]

        # 4. Sudah Dikembalikan (Status 'Dikembalikan')
        cursor.execute("SELECT COUNT(*) FROM peminjaman WHERE status = 'Dikembalikan'")
        sudah_dikembalikan = cursor.fetchone()[0]

        # 5. Distribusi Stok Buku (Untuk grafik batang horizontal)
        cursor.execute("SELECT judul, stok FROM buku ORDER BY judul ASC")
        distribusi_buku = [{'judul': r[0], 'stok': r[1]} for r in cursor.fetchall()]

    # Kirim seluruh data ringkasan statistik ke template baru
    konteks = {
        'total_buku': total_buku,
        'total_judul': total_judul,
        'sedang_dipinjam': sedang_dipinjam,
        'sudah_dikembalikan': sudah_dikembalikan,
        'distribusi_buku': distribusi_buku,
    }
    return render(request, 'index_dashboard.html', konteks) # <-- NAMA FILE DIGANTI DI SINI
# 1. FITUR DETAIL BUKU

# Tambahkan fungsi ini di dalam views.py kamu!
def daftar_buku_lama(request):
    with connection.cursor() as cursor:
        # Ambil seluruh data dari tabel buku menggunakan Raw SQL
        cursor.execute("SELECT * FROM buku ORDER BY id ASC")
        kolom_buku = [col[0] for col in cursor.description]
        data_buku = [dict(zip(kolom_buku, row)) for row in cursor.fetchall()]
        
    # Kirim data ke file HTML katalog lama kamu (dashboard.html)
    konteks = {
        'list_buku': data_buku,
    }
    return render(request, 'dashboard.html', konteks)

def detail_buku(context, id_buku):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM buku WHERE id = %s", [id_buku])
        kolom = [col[0] for col in cursor.description]
        buku = dict(zip(kolom, cursor.fetchone()))
    return render(context, 'detail.html', {'buku': buku})

# 2. FITUR EDIT BUKU
def edit_buku(context, id_buku):
    with connection.cursor() as cursor:
        if context.method == 'POST':
            judul = context.POST['judul']
            pengarang = context.POST['pengarang']
            kategori = context.POST['kategori']
            tahun_terbit = context.POST['tahun_terbit']
            rak = context.POST['rak']
            penerbit = context.POST['penerbit']
            stok = context.POST['stok']
            isbn = context.POST.get('isbn', '')
            deskripsi = context.POST.get('deskripsi', '')
            
            # KUNCI 1: Pastikan SET menggunakan nama kolom yang sesuai, 
            # dan WHERE menggunakan kolom 'id' (sesuai database kamu)
            cursor.execute(
                """
                UPDATE buku 
                SET judul = %s, pengarang = %s, kategori = %s, tahun_terbit = %s, rak = %s, penerbit = %s, stok = %s, isbn = %s, deskripsi = %s
                WHERE id = %s
                """,
                [judul, pengarang, kategori, tahun_terbit, rak, penerbit, stok, isbn, deskripsi, id_buku]
            )
            return redirect('dashboard')
        
        # KUNCI 2: Pastikan mengambil data lama berdasarkan kolom 'id'
        cursor.execute("SELECT * FROM buku WHERE id = %s", [id_buku])
        kolom = [col[0] for col in cursor.description]
        buku = dict(zip(kolom, cursor.fetchone()))

    return render(context, 'edit.html', {'buku': buku})
# 3. FITUR HAPUS BUKU
def hapus_buku(context, id_buku):
    with connection.cursor() as cursor:
        # Jika admin menekan tombol konfirmasi "Hapus" (POST)
        if context.method == 'POST':
            cursor.execute("DELETE FROM buku WHERE id = %s", [id_buku])
            return redirect('dashboard')
        
        # Jika baru memuat halaman konfirmasi (GET), ambil info judul bukunya
        cursor.execute("SELECT id, judul FROM buku WHERE id = %s", [id_buku])
        kolom = [col[0] for col in cursor.description]
        buku = dict(zip(kolom, cursor.fetchone()))

    return render(context, 'hapus.html', {'buku': buku})

def tambah_buku(context):
    if context.method == 'POST':
        judul = context.POST['judul']
        pengarang = context.POST['pengarang']
        kategori = context.POST['kategori']
        penerbit = context.POST['penerbit']
        tahun_terbit = context.POST['tahun_terbit']
        rak = context.POST['rak']
        stok = context.POST['stok']
        isbn = context.POST.get('isbn', '')
        deskripsi = context.POST.get('deskripsi', '')
        
        with connection.cursor() as cursor:
            # Query INSERT ke database PostgreSQL (kolom 'id' akan otomatis terisi jika serial/auto-increment)
            cursor.execute(
                """
                INSERT INTO buku (judul, pengarang, kategori, penerbit, tahun_terbit, rak, stok, isbn, deskripsi)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                [judul, pengarang, kategori, penerbit, tahun_terbit, rak, stok, isbn, deskripsi]
            )
        return redirect('dashboard')
        
    return render(context, 'tambah.html')


# 1. DAFTAR SISWA (Pendek & Bersih lewat bantuan SQL)
def daftar_siswa(context):
    with connection.cursor() as cursor:
        # SQL langsung mengubah true/false jadi teks 'Aktif'/'Tidak Aktif'
        cursor.execute("""
            SELECT id, nama, kelas, nis, 
                   CASE WHEN status = true THEN 'Aktif' ELSE 'Tidak Aktif' END AS status 
            FROM siswa ORDER BY id ASC
        """)
        kolom = [col[0] for col in cursor.description]
        list_siswa = [dict(zip(kolom, row)) for row in cursor.fetchall()]
    return render(context, 'siswa/daftar.html', {'list_siswa': list_siswa})

# 2. TAMBAH SISWA
def tambah_siswa(context):
    if context.method == 'POST':
        nama = context.POST['nama']
        kelas = context.POST['kelas']
        nis = context.POST['nis']
        status = True if context.POST['status'] == 'Aktif' else False
        
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO siswa (nama, kelas, nis, status) VALUES (%s, %s, %s, %s)",
                [nama, kelas, nis, status]
            )
        return redirect('daftar_siswa')
    return render(context, 'siswa/tambah.html')

# 3. EDIT SISWA
def edit_siswa(context, id_siswa):
    with connection.cursor() as cursor:
        if context.method == 'POST':
            nama = context.POST['nama']
            kelas = context.POST['kelas']
            nis = context.POST['nis']
            status = True if context.POST['status'] == 'Aktif' else False
            
            cursor.execute(
                "UPDATE siswa SET nama = %s, kelas = %s, nis = %s, status = %s WHERE id = %s",
                [nama, kelas, nis, status, id_siswa]
            )
            return redirect('daftar_siswa')
        
        cursor.execute("SELECT id, nama, kelas, nis, CASE WHEN status = true THEN 'Aktif' ELSE 'Tidak Aktif' END AS status FROM siswa WHERE id = %s", [id_siswa])
        kolom = [col[0] for col in cursor.description]
        siswa = dict(zip(kolom, cursor.fetchone()))
    return render(context, 'siswa/edit.html', {'siswa': siswa})

def detail_siswa(request, id_siswa):
    with connection.cursor() as cursor:
        # 1. AMBIL DATA UTAMA SISWA
        cursor.execute("""
            SELECT id, nama, kelas, nis, 
                   CASE WHEN status = true THEN 'Aktif' ELSE 'Tidak Aktif' END AS status 
            FROM siswa WHERE id = %s
        """, [id_siswa])
        kolom = [col[0] for col in cursor.description]
        siswa_row = cursor.fetchone()
        
        if not siswa_row:
            return redirect('daftar_siswa')
            
        siswa = dict(zip(kolom, siswa_row))

        # 2. HITUNG TOTAL PEMINJAMAN (Hanya hitung yang berstatus 'Dipinjam')
        # Jadi kalau semua sudah dikembalikan, total peminjaman otomatis jadi 0 kembali sesuai keinginanmu.
        cursor.execute("""
            SELECT COUNT(*) FROM peminjaman 
            WHERE siswa_id = %s AND status = 'Dipinjam'
        """, [id_siswa])
        total_peminjaman = cursor.fetchone()[0]

        # 3. AMBIL PEMINJAMAN AKTIF
        # Kita samakan string statusnya menggunakan 'Dipinjam'
        cursor.execute("""
            SELECT b.judul 
            FROM peminjaman p
            INNER JOIN buku b ON p.buku_id = b.id
            WHERE p.siswa_id = %s AND p.status = 'Dipinjam'
        """, [id_siswa])
        
        buku_dipinjam = [row[0] for row in cursor.fetchall()]
        jumlah_buku_aktif = len(buku_dipinjam)

    # Kirim data ke HTML
    konteks = {
        'siswa': siswa,
        'total_peminjaman': total_peminjaman,
        'buku_dipinjam': buku_dipinjam,
        'jumlah_buku_aktif': jumlah_buku_aktif,
    }
    return render(request, 'siswa/detail.html', konteks)

# 5. HAPUS SISWA
def hapus_siswa(context, id_siswa):
    with connection.cursor() as cursor:
        if context.method == 'POST':
            cursor.execute("DELETE FROM siswa WHERE id = %s", [id_siswa])
            return redirect('daftar_siswa')
        
        cursor.execute("SELECT id, nama FROM siswa WHERE id = %s", [id_siswa])
        kolom = [col[0] for col in cursor.description]
        siswa = dict(zip(kolom, cursor.fetchone()))
    return render(context, 'siswa/hapus.html', {'siswa': siswa})


# ====================================================================
# 1. HALAMAN DAFTAR PEMINJAMAN 
# ====================================================================
def daftar_peminjaman(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                p.id, 
                s.nama AS nama_siswa, 
                b.judul AS judul_buku, 
                p.tanggal_pinjam, 
                p.jatuh_tempo, 
                p.keperluan, 
                p.status,
                p.petugas
            FROM peminjaman p
            INNER JOIN siswa s ON p.siswa_id = s.id
            INNER JOIN buku b ON p.buku_id = b.id
            ORDER BY p.id ASC
        """)
        rows = cursor.fetchall()
        
        peminjaman_list = []
        for row in rows:
            peminjaman_list.append({
                'id': row[0],
                'nama_siswa': row[1],
                'judul_buku': row[2],
                'tanggal_pinjam': row[3],
                'jatuh_tempo': row[4],
                'keperluan': row[5],
                'status': row[6],
                'petugas': row[7] if row[7] else '-' 
            })
            
    return render(request, 'peminjaman/daftar_peminjaman.html', {'peminjaman_list': peminjaman_list})


# ====================================================================
# 2. HALAMAN TAMBAH PEMINJAMAN (FORM DROPDOWN OTOMATIS)
# ====================================================================
def tambah_peminjaman(request):
    if request.method == 'POST':
        siswa_id = request.POST.get('siswa_id')
        buku_id = request.POST.get('buku_id')
        tanggal_pinjam = request.POST.get('tanggal_pinjam')
        jatuh_tempo = request.POST.get('jatuh_tempo')
        keperluan = request.POST.get('keperluan')  # Menangkap hasil pilihan dropdown
        catatan = request.POST.get('catatan', '')  
        nama_petugas = request.POST.get('petugas', '')# BARU: Menangkap tulisan dari textarea catatan
        

        with connection.cursor() as cursor:
            # Query INSERT diperbarui untuk menyertakan kolom catatan (pastikan di psql kolom ini sudah ada)
            cursor.execute("""
                INSERT INTO peminjaman (siswa_id, buku_id, tanggal_pinjam, jatuh_tempo, keperluan, catatan, status, petugas)
                VALUES (%s, %s, %s, %s, %s, %s, 'Dipinjam', %s)
            """, [siswa_id, buku_id, tanggal_pinjam, jatuh_tempo, keperluan, catatan, nama_petugas])
            
            # Otomatis mengurangi stok buku
            cursor.execute("""
                UPDATE buku SET stok = stok - 1 WHERE id = %s
            """, [buku_id])
            
        return redirect('daftar_peminjaman')

    # --- JALUR GET (MEMUAT HALAMAN FORM) ---
    hari_ini = datetime.now().date()
    jatuh_tempo_default = hari_ini + timedelta(days=7)

    with connection.cursor() as cursor:
        # Ambil daftar siswa untuk dropdown
        cursor.execute("SELECT id, nama, kelas FROM siswa ORDER BY nama ASC")
        siswa_rows = cursor.fetchall()
        siswa_list = [{'id': r[0], 'nama': r[1], 'kelas': r[2]} for r in siswa_rows]

        # Ambil daftar buku untuk dropdown
        cursor.execute("SELECT id, judul, stok FROM buku WHERE stok > 0 ORDER BY judul ASC")
        buku_rows = cursor.fetchall()
        buku_list = [{'id': r[0], 'judul': r[1], 'stok': r[2]} for r in buku_rows]

    context = {
        'siswa_list': siswa_list,
        'buku_list': buku_list,
        'hari_ini': hari_ini.strftime('%Y-%m-%d'),
        'jatuh_tempo': jatuh_tempo_default.strftime('%Y-%m-%d'),
    }
    return render(request, 'peminjaman/tambah_peminjaman.html', context)

# ====================================================================
# 3. FUNGSI LOGIKA TOMBOL KEMBALIKAN BUKU
# ====================================================================
# ====================================================================
def kembalikan_buku(request, id_peminjaman):
    with connection.cursor() as cursor:
        # Kita ubah menjadi 'Dikembalikan' agar rapi dan konsisten dengan pengecekan status
        cursor.execute("""
            UPDATE peminjaman 
            SET status = 'Dikembalikan' 
            WHERE id = %s
        """, [id_peminjaman])
        
    return redirect('daftar_peminjaman')

# ====================================================================
# 4. FUNGSI BARU: HAPUS REKORD DATA PEMINJAMAN DENGAN KONFIRMASI
# ====================================================================
def hapus_peminjaman(request, id_peminjaman):
    with connection.cursor() as cursor:
        # Jika tombol merah "Hapus" ditekan (POST)
        if request.method == 'POST':
            cursor.execute("DELETE FROM peminjaman WHERE id = %s", [id_peminjaman])
            return redirect('daftar_peminjaman')
        
        # Jika baru memuat halaman konfirmasi (GET), ambil info peminjaman untuk ditampilkan
        cursor.execute("""
            SELECT p.id, s.nama, b.judul 
            FROM peminjaman p
            INNER JOIN siswa s ON p.siswa_id = s.id
            INNER JOIN buku b ON p.buku_id = b.id
            WHERE p.id = %s
        """, [id_peminjaman])
        
        row = cursor.fetchone()
        if not row:
            return redirect('daftar_peminjaman')
            
        peminjaman = {
            'id': row[0],
            'nama_siswa': row[1],
            'judul_buku': row[2]
        }
        
    return render(request, 'peminjaman/hapus_peminjaman.html', {'peminjaman': peminjaman})