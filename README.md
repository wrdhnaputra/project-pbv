# project-pbv
To Do List Drakor

👨‍🎓 Author

Nama: Restu Wardhana Putra
Jurusan: Teknik Elektro
Program Studi: Teknik Informatika
Mata Kuliah: Pemrograman Visual
Tahun: 2026

📺 To-Do List Drakor (PySide6 + TMDB API)

Aplikasi desktop berbasis Python & PySide6 untuk mengelola daftar tontonan Drama Korea (Drakor).
Aplikasi ini mendukung fitur login multi-user, role admin & user, integrasi TMDB API, serta tampilan UI modern.

Project ini dibuat sebagai Final Project / UAS Pemrograman Visual.

🚀 Fitur Utama
👤 Autentikasi

Login & Register user

Role Admin & User

Sistem peringatan dari Admin

🎬 Manajemen Drakor

Tambah, edit, hapus drakor

Status otomatis:

Akan Ditonton

Sedang Ditonton

Selesai

Tandai drakor sebagai Favorit

Poster drakor bisa diklik (preview)

🔎 Integrasi TMDB API

Cari drakor langsung dari TMDB

Otomatis mengambil:

Judul (Bahasa Inggris)

Total episode

Genre

Poster

User hanya mengisi:

Episode terakhir

Favorit

📋 List Drakor

Tampilan list modern menggunakan QListWidget

Menampilkan poster, judul, genre, status, dan episode

Fitur pencarian drakor

👑 Fitur Admin

Melihat daftar user

Memberi peringatan ke user

Menghapus user beserta seluruh data drakor

🛠️ Teknologi yang Digunakan

Python 3.12

PySide6 (Qt for Python)

SQLite3

TMDB API

Qt Widgets & QSS Styling

📁 Struktur Folder
Final Project/

│

├── posters/               # Poster drakor (TMDB)

├── database.py            # Koneksi & query database

├── tmdb_api.py            # Integrasi TMDB API

├── layout.py              # Main aplikasi

├── logo.png               # Logo aplikasi

├── README.md              # Dokumentasi

🔑 Konfigurasi TMDB API

Buat akun di https://www.themoviedb.org

Ambil API Key

Masukkan ke file tmdb_api.py

API_KEY = "****"

▶️ Cara Menjalankan Aplikasi

Install dependency:

pip install PySide6 requests


Jalankan aplikasi:

python layout.py

🧪 Akun Default (Jika Ada)
Role	Username	Password
Admin	admin	admin
📸 Screenshot Aplikasi

(Tambahkan screenshot aplikasi di sini untuk nilai plus GitHub)

📚 Catatan Pengembangan

Poster disimpan secara lokal untuk efisiensi

Status drakor otomatis berdasarkan episode

UI dibuat responsif & user-friendly

Cocok sebagai referensi CRUD Desktop App dengan API

📄 Lisensi

Project ini dibuat untuk keperluan akademik dan bebas digunakan untuk pembelajaran.
