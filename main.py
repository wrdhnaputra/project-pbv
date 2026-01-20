import os
import shutil
import sys

from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QSpinBox, QFileDialog,
    QPushButton, QTableWidget, QTableWidgetItem,
    QCheckBox, QMessageBox, QLabel, QFrame, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap
from database import connect_db, create_tables, insert_default_data
from tmdb_api import search_drakor



# ================= WELCOME / LOGIN =================
class WelcomeWindow(QWidget):
    def __init__(self):
        super().__init__()

        create_tables()
        insert_default_data()

        self.setWindowTitle("Login")
        self.setFixedSize(360, 500)
        self.setStyleSheet("""
                           background-color:#f4f6f8;
                            color:#222;""")

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        logo = QLabel(alignment=Qt.AlignCenter)
        pixmap = QPixmap(os.path.join(os.path.dirname(__file__), "logo.png"))
        logo.setPixmap(pixmap.scaled(260, 260, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        title = QLabel("To-Do List Drakor", alignment=Qt.AlignCenter)
        title.setStyleSheet("font-size:22px; font-weight:bold;")

        subtitle = QLabel("Kelola tontonan drama Korea kamu", alignment=Qt.AlignCenter)
        subtitle.setStyleSheet("color:gray;")

        self.inputUser = QLineEdit(placeholderText="Username")
        self.inputUser.setStyleSheet("""
            background:#ffffff;
            color:#000000;
            padding:8px;
            border-radius:8px;
            border:1px solid #ccc;
        """)


        self.inputPass = QLineEdit(placeholderText="Password")
        self.inputPass.setEchoMode(QLineEdit.Password)
        self.inputPass.setStyleSheet("""
            background:#ffffff;
            color:#000000;
            padding:8px;
            border-radius:8px;
            border:1px solid #ccc;
        """)


        btnLogin = QPushButton("Login")
        btnLogin.setStyleSheet("""
            QPushButton {
            background:#1976d2;
            color:white;
            padding:10px;
            border-radius:20px;
            font-weight:bold;
        }
        QPushButton:hover {
            background:#1565c0;
        }
        """)
        btnLogin.clicked.connect(self.login_user)

        btnRegister = QPushButton("Register")
        btnRegister.setStyleSheet("""
            QPushButton {
                background:#4caf50;
                color:white;
                padding:10px;
                border-radius:20px;
                font-weight:bold;
            }
            QPushButton:hover {
            background:#43a047;
            }
        """)
        btnRegister.clicked.connect(self.register_user)


        layout.addStretch()
        layout.addWidget(logo)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.inputUser)
        layout.addWidget(self.inputPass)
        layout.addWidget(btnLogin)
        layout.addWidget(btnRegister)
        layout.addStretch()

    #======== Login User ========
    def login_user(self):
        conn = connect_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT id_user, role FROM user WHERE username=? AND password=?",
            (self.inputUser.text(), self.inputPass.text())
        )
        result = cur.fetchone()
        conn.close()

        if result:
            id_user = result[0]
            role = result[1]

            conn = connect_db()
            cur = conn.cursor()
            cur.execute("""
                    SELECT pesan, tanggal FROM peringatan_admin
                    WHERE id_user=?
            """, (id_user,))
            warnings = cur.fetchall()
            conn.close()

            if warnings:
                pesan = "\n\n".join(
                    [f"- {w[0]} (Tanggal: {w[1]})" for w in warnings])
                QMessageBox.warning(
                    self,
                    "⚠️ Peringatan dari Admin",
                    pesan
                )   

            self.menu = MenuWindow(role, id_user)
            self.menu.show()
            self.close()
        else:
            QMessageBox.warning(self, "Login Gagal", "Username atau password salah!")

    def register_user(self):
        username = self.inputUser.text().strip()
        password = self.inputPass.text().strip()

        if not username or not password:
            QMessageBox.warning(
                self,
                "Register Gagal",
                "Username dan Password tidak boleh kosong!"
            )
            return
        
        conn = connect_db()
        cur = conn.cursor()

        cur.execute(
            "SELECT id_user FROM user WHERE username=?",
            (username,)
        )
        if cur.fetchone():
            QMessageBox.warning(
                self,
                "Register Gagal",
                "Username sudah terdaftar, silahkan gunakan username lain."
            )
            conn.close()
            return

        cur.execute("""
            INSERT INTO user (username, password, role)
            VALUES (?, ?, ?)
        """, (username, password, "user"))

        conn.commit()
        conn.close()

        QMessageBox.information(
            self,
            "Register Berhasil",
            "Akun berhasil dibuat!"
        )

        self.inputUser.clear()
        self.inputPass.clear()

# ================= MENU =================
class MenuWindow(QWidget):
    def __init__(self, role, id_user):
        super().__init__()
        self.role = role
        self.id_user = id_user

        self.setWindowTitle("Menu Utama")
        self.setFixedSize(400, 350)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        title = QLabel("Menu Utama", alignment=Qt.AlignCenter)
        title.setStyleSheet("font-size:22px;font-weight:bold;color:#222")

        btnForm = QPushButton("➕ Input Drakor")
        btnList = QPushButton("📋 List Drakor")
        btnLogout = QPushButton("🚪 Logout")

        for btn in (btnForm, btnList, btnLogout):
            btn.setStyleSheet("""
                QPushButton {
                    background:#1e1e1e;
                    color:white;
                    padding:12px;
                    border-radius:15px;
                }
                QPushButton:hover {background:#333;}
            """)

        btnForm.clicked.connect(self.open_form)
        btnList.clicked.connect(self.open_list)
        btnLogout.clicked.connect(self.logout)

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(btnForm)
        layout.addWidget(btnList)

        if self.role == "admin":
            btnAdmin = QPushButton("👤 Lihat Jumlah User")
            btnAdmin.setStyleSheet("""
                QPushButton {background:#1e1e1e;color:white;padding:12px;border-radius:15px;}
            """)
            btnAdmin.clicked.connect(self.open_user_list)
            layout.addWidget(btnAdmin)

        layout.addWidget(btnLogout)
        layout.addStretch()

    def logout(self):
        reply = QMessageBox.question(
            self, "Logout", "Yakin ingin logout?",
            QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.welcome = WelcomeWindow()
            self.welcome.show()
            self.close()

    def open_user_list(self):
        self.user_window = UserListWindow()
        self.user_window.show()

    def open_form(self):
        self.form = FormWindow(self.id_user)
        self.form.show()

    def open_list(self):
        self.list = ListWindow(self.id_user)
        self.list.show()

    def show_admin_info(self):
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM user")
        total = cur.fetchone()[0]
        conn.close()
        QMessageBox.information(self, "Admin", f"Total user terdaftar: {total}")

class UserListWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Manajemen User")
        self.resize(550, 400)

        layout = QVBoxLayout(self)

        title = QLabel("Manajemen User", alignment=Qt.AlignCenter)
        title.setStyleSheet("font-size:18px;font-weight:bold;")
        layout.addWidget(title)

        # ===== SEARCH =====
        self.search = QLineEdit()
        self.search.setPlaceholderText("Cari username...")
        self.search.textChanged.connect(self.search_user)
        layout.addWidget(self.search)

        # ===== TABLE =====
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(
            ["ID User", "Username", "Role"]
        )
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.cellClicked.connect(self.select_user)

        layout.addWidget(self.table)

        # ===== BUTTON =====
        btns = QHBoxLayout()
        btnWarning = QPushButton("⚠️ Beri Peringatan")
        btnDelete = QPushButton("🗑 Hapus User")

        btnWarning.clicked.connect(self.peringatan_admin)
        btnDelete.clicked.connect(self.delete_user)

        btns.addWidget(btnWarning)
        btns.addWidget(btnDelete)
        layout.addLayout(btns)

        self.selected_id = None
        self.load_users()

    # ================= LOAD =================
    def load_users(self):
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT id_user, username, role FROM user")
        data = cur.fetchall()
        conn.close()

        self.table.setRowCount(0)
        for r, u in enumerate(data):
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(str(u[0])))
            self.table.setItem(r, 1, QTableWidgetItem(u[1]))
            self.table.setItem(r, 2, QTableWidgetItem(u[2]))

    # ================= SELECT =================
    def select_user(self, row, col):
        self.selected_id = int(self.table.item(row, 0).text())
        self.selected_username = self.table.item(row, 1).text()
        self.selected_role = self.table.item(row, 2).text()

    # ================= SEARCH =================
    def search_user(self, text):
        conn = connect_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT id_user, username, role FROM user WHERE username LIKE ?",
            (f"%{text}%",)
        )
        data = cur.fetchall()
        conn.close()

        self.table.setRowCount(0)
        for r, u in enumerate(data):
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(str(u[0])))
            self.table.setItem(r, 1, QTableWidgetItem(u[1]))
            self.table.setItem(r, 2, QTableWidgetItem(u[2]))

    # ================= WARNING =================
    def peringatan_admin(self):
        if not self.selected_id:
            QMessageBox.warning(self, "Peringatan", "Pilih user terlebih dahulu")
            return

        if self.selected_role == "admin":
            QMessageBox.warning(self, "Ditolak", "Admin tidak bisa diberi peringatan")
            return
        
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO peringatan_admin (id_user, pesan, tanggal)
            VALUES (?, ?, ?)
        """, (
            self.selected_id,
            "Peringatan dari Admin: Harap patuhi aturan penggunaan aplikasi.",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        conn.commit()
        conn.close()

        QMessageBox.information(
            self,
            "Peringatan Dikirim",
            f"⚠️ User '{self.selected_username}' telah diberi peringatan!"
        )

    # ================= DELETE =================
    def delete_user(self):
        if not self.selected_id:
            QMessageBox.warning(self, "Hapus", "Pilih user terlebih dahulu")
            return

        if self.selected_role == "admin":
            QMessageBox.warning(self, "Ditolak", "Admin tidak bisa dihapus")
            return

        reply = QMessageBox.question(
            self,
            "Konfirmasi",
            f"Hapus user '{self.selected_username}' beserta semua drakornya?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            conn = connect_db()
            cur = conn.cursor()

            # hapus drakor user
            cur.execute("DELETE FROM drakor WHERE id_user=?", (self.selected_id,))
            # hapus user
            cur.execute("DELETE FROM user WHERE id_user=?", (self.selected_id,))

            conn.commit()
            conn.close()

            self.selected_id = None
            self.load_users()

            QMessageBox.information(self, "Sukses", "User berhasil dihapus")

class ClickableLabel(QLabel):
    def mousePressEvent(self, event):
        if self.pixmap():
            preview = QLabel()
            preview.setWindowTitle("Preview Poster")
            preview.setPixmap(self.pixmap())
            preview.setAlignment(Qt.AlignCenter)
            preview.setMinimumSize(400, 600)
            preview.show()

            # simpan reference agar tidak langsung hilang
            self._preview = preview


class FormWindow(QWidget):
    def __init__(self, id_user, list_window=None):
        super().__init__()
        self.id_user = id_user
        self.list_window = list_window
        self.selected_id = None

        self.setWindowTitle("Input Drakor")
        self.setFixedSize(650, 600)

        layout = QFormLayout(self)

        # ===== HEADER =====
        header = QFrame()
        header.setStyleSheet("""
        QFrame {
            background-color: #f5f5f5;
            border-radius: 15px;
        }
        """)
        header.setFixedHeight(180)

        

        self.poster = ClickableLabel("No\nPoster")
        self.poster.setFixedSize(120, 160)
        self.poster.setAlignment(Qt.AlignCenter)
        self.poster.setStyleSheet("""
            QLabel {
                background-color: #bdbdbd;
                border-radius: 12px;
                font-size: 12px;
                color: #333;
            }
        """)


        lblTitle = QLabel("📺 INPUT DRAKOR")
        lblTitle.setAlignment(Qt.AlignLeft)
        lblTitle.setStyleSheet("""
            color: #212121;
            font-size: 22px;
            font-weight: bold;
        """)

        lblSub = QLabel("Kelola daftar tontonan drama Korea kamu")
        lblSub.setAlignment(Qt.AlignLeft)
        lblSub.setWordWrap(True)
        lblSub.setStyleSheet("""
                color: #424242;
                font-size: 14px;
        """)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 15, 20, 15)
        header_layout.setSpacing(20)

        text_layout = QVBoxLayout()
        text_layout.addWidget(lblTitle)
        text_layout.addWidget(lblSub)
        text_layout.addStretch()

        header_layout.addWidget(self.poster)
        header_layout.addLayout(text_layout)

        layout.addRow(header)

        self.judul = QLineEdit()
        self.genre = QComboBox()
        self.total = QSpinBox()
        self.status = QComboBox()
        self.episode = QSpinBox()
        self.episode.valueChanged.connect(
            self.update_status_otomatis)
        self.total.valueChanged.connect(
            lambda val: self.episode.setMaximum(val)
        )
        self.status.setEnabled(False)
        self.favorit = QCheckBox("Favorit")
        self.genre.setEditable(False)
        self.status.setEditable(False)

        self.total.setMinimum(1)

        btnSimpan = QPushButton("Simpan Data")
        btnSimpan.clicked.connect(self.simpan_drakor)
        btnTMDB = QPushButton("Cari di TMDB")
        btnTMDB.clicked.connect(self.cari_drakor_tmdb)

        layout.addRow("Judul", self.judul)
        layout.addRow("Genre", self.genre)
        layout.addRow("Total Episode", self.total)
        layout.addRow("Episode Terakhir", self.episode)
        layout.addRow("Status", self.status)
        layout.addRow(self.favorit)
        layout.addRow(btnSimpan)
        layout.addRow(btnTMDB)

        self.load_genre()
        self.load_status()

    def load_genre(self):
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT id_genre, nama_genre FROM genre")
        self.genre.clear()
        for i, n in cur.fetchall():
            self.genre.addItem(n, i)
        conn.close()

    def load_status(self):
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT id_status, nama_status FROM status")
        self.status.clear()
        for i, n in cur.fetchall():
            self.status.addItem(n, i)
        conn.close()

    def update_status_otomatis(self):
        ep_now = self.episode.value()
        ep_total = self.total.value()

        if ep_now == 0:
            status_name = "Akan Ditonton"
        elif ep_now == ep_total:
            status_name = "Selesai"
        else:
            status_name = "Sedang Ditonton"

        for i in range(self.status.count()):
            if self.status.itemText(i) == status_name:
                self.status.setCurrentIndex(i)
                break

    def simpan_drakor(self):
        if not self.judul.text().strip():
            QMessageBox.warning(self, "Validasi", "Judul wajib diisi")
            return
        
        if self.episode.value() > self.total.value():
            QMessageBox.warning(
                self,
                "Validasi Episode",
                "Episode terakhir tidak boleh lebih besar dari total episode",
                "Silahkan Diperbaiki"
            )
            return
        
        if self.genre.currentData() is None:
            QMessageBox.warning(self, "Validasi", "Genre harus dipilih dari daftar")
            return

        if self.status.currentData() is None:
            QMessageBox.warning(self, "Validasi", "Status harus dipilih dari daftar")
            return


        conn = connect_db()
        cur = conn.cursor()

        if self.selected_id:  # EDIT
            cur.execute("""
                UPDATE drakor SET
                    judul=?, total_episode=?, episode_terakhir=?,
                    id_genre=?, id_status=?, favorit=?, poster_path=?
                WHERE id_drakor=?
            """,
             (
                self.judul.text(),
                self.total.value(),
                self.episode.value(),
                self.genre.currentData(),
                self.status.currentData(),
                1 if self.favorit.isChecked() else 0,
                getattr(self, "current_poster_path", None),
                self.selected_id
            ))
        else:  # TAMBAH
            cur.execute("""
                INSERT INTO drakor
                (judul, total_episode, episode_terakhir,
                 id_genre, id_status, favorit, id_user, poster_path)
                VALUES (?,?,?,?,?,?,?,?)
            """, 
            (
                self.judul.text(),
                self.total.value(),
                self.episode.value(),
                self.genre.currentData(),
                self.status.currentData(),
                1 if self.favorit.isChecked() else 0,
                self.id_user,
                getattr(self, "current_poster_path", None)
            ))

        conn.commit()
        conn.close()

        if self.list_window:
            self.list_window.load_drakor()

        QMessageBox.information(
            self,
            "Sukses",
            "Drakor berhasil disimpan!"
        )
        self.poster.setText("No\nPoster")
        self.poster.setPixmap(QPixmap())
        self.current_poster_path = None

        self.reset_form()

    def cari_drakor_tmdb(self):
        keyword = self.judul.text().strip()

        if not keyword:
            QMessageBox.warning(
                self,
                "Cari Drakor",
                "Masukkan judul drakor terlebih dahulu."
            )
            return

        data = search_drakor(keyword)

        if not data.get("results"):
            QMessageBox.information(
                self,
                "TMDB",
                "Drakor tidak ditemukan di TMDB."
            )
            return
        drakor = None
        for item in data["results"]:
            if "KR" in item.get("origin_country", []):
                drakor = item
                break

        if not drakor:
            QMessageBox.information(
                self,
                "TMDB",
                "Drama Korea tidak ditemukan."
            )
            return
    
        from tmdb_api import gettv_detail
        detail = gettv_detail(drakor["id"])

        # ===== POSTER TMDB =====
        poster_path = detail.get("poster_path")
        if poster_path:  # Jika poster ada → download & simpan lokal
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"

            from urllib.request import urlopen
            data = urlopen(poster_url).read()

            # Buat folder poster
            base = os.path.abspath(os.path.dirname(__file__))
            folder = os.path.join(base, "posters")

            if not os.path.exists(folder):
                os.makedirs(folder)

            filename = poster_path.replace("/", "")
            local_path = os.path.join(folder, filename)
            with open(local_path, "wb") as f:
                f.write(data)

            self.current_poster_path = os.path.join("posters", filename)

            self.poster.setPixmap(QPixmap(local_path).scaled(
                110, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))


        # Judul
        self.judul.setText(detail["name"])

        # Total episode (AKURAT)
        total_episode = detail.get("number_of_episodes", 1)
        self.total.setValue(total_episode)
        self.total.setEnabled(False)

        # Genre (DETAIL TV)
        genres = [g["name"] for g in detail.get("genres", [])]
        self.set_genre_by_name(genres)
        self.genre.setEnabled(False)

        QMessageBox.information(
            self,
            "TMDB",
            f"'{detail['name']}' berhasil dimuat dari TMDB.\n"
            "Silakan isi episode terakhir dan favorit."
        )

    def set_genre_by_name(self, genres):
        for g in genres:
            for i in range(self.genre.count()):
                if self.genre.itemText(i).lower() in g.lower():
                    self.genre.setCurrentIndex(i)
                    return

    def reset_form(self):
        self.judul.clear()
        self.total.setValue(1)
        self.episode.setValue(0)
        self.favorit.setChecked(False)
        self.selected_id = None

class DrakorItem(QFrame):
    def __init__(self, judul, genre, episode, status, favorit, poster=None):
        super().__init__()
        self.setStyleSheet("""
        QFrame {
            background: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 15px;
        }
        QFrame:hover {
            background: #f5f5f5;
        }
        """)
        self.setFixedHeight(120)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        lblPoster = QLabel()
        lblPoster.setFixedSize(80, 100)
        lblPoster.setAlignment(Qt.AlignCenter)

        if poster:
            lblPoster.setPixmap(poster.scaled(
                80, 100, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            ))
        else:
            lblPoster.setText("No\nPoster")
            lblPoster.setStyleSheet("background:#ccc;border-radius:10px;")

        text = QLabel(
            f"<b>{judul}</b><br>"
            f"{genre}<br>"
            f"{episode} • {status} {'⭐' if favorit else ''}"
        )
        text.setWordWrap(True)

        layout.addWidget(lblPoster)
        layout.addWidget(text)


class ListWindow(QWidget):
    def __init__(self, id_user):
        super().__init__()
        self.id_user = id_user
        self.selected_id = None

        self.setWindowTitle("List Drakor")
        self.resize(700, 400)

        layout = QVBoxLayout(self)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Cari judul...")
        self.search.textChanged.connect(self.search_drakor)

        self.list = QListWidget()
        self.list.setSpacing(8)
        self.list.setStyleSheet("""
            QListWidget {
                background: #fafafa;
                border: none;
                padding: 8px;
            }
        """)

        self.list.itemClicked.connect(lambda: self.select_row())
        layout.addWidget(self.search)
        layout.addWidget(self.list)

        btns = QHBoxLayout()
        btnHapus = QPushButton("Hapus")
        btnReset = QPushButton("Hapus Semua")

        btnHapus.clicked.connect(self.hapus_drakor)
        btnReset.clicked.connect(self.reset_drakor)

        btns.addWidget(btnHapus)
        btns.addWidget(btnReset)

        layout.addLayout(btns)

        # ===== FORM EDIT (KHUSUS LIST) =====
        self.editJudul = QLineEdit()
        self.editJudul.setReadOnly(True)
        self.editGenre = QComboBox()
        self.editGenre.setEnabled(False)
        self.editStatus = QComboBox()
        self.editStatus.setEnabled(False)
        self.editTotal = QSpinBox()
        self.editTotal.setReadOnly(True)
        self.editTotal.setMinimum(1)
        self.editEpisode = QSpinBox()
        self.editEpisode.setEnabled(False)
        self.editEpisode.setMinimum(0)
        self.editTotal.valueChanged.connect(
            lambda val: self.editEpisode.setMaximum(val)
        )

        self.editFavorit = QCheckBox("Favorit")
        self.editEpisode = QSpinBox()
        self.editEpisode.setMinimum(0)

        btnUpdate = QPushButton("Update Data")
        btnUpdate.clicked.connect(self.update_drakor)

        formEdit = QFormLayout()
        formEdit.addRow("Judul", self.editJudul)
        formEdit.addRow("Genre", self.editGenre)
        formEdit.addRow("Status", self.editStatus)
        formEdit.addRow("Total Episode", self.editTotal)
        formEdit.addRow("Episode Terakhir", self.editEpisode)
        formEdit.addRow(btnUpdate)
        layout.addLayout(formEdit)

        self.load_genre_status()
        self.load_drakor()

    def load_genre_status(self):
        conn = connect_db()
        cur = conn.cursor()

        self.editGenre.clear()
        cur.execute("SELECT id_genre, nama_genre FROM genre")
        for i, n in cur.fetchall():
            self.editGenre.addItem(n, i)

        self.editStatus.clear()
        cur.execute("SELECT id_status, nama_status FROM status")
        for i, n in cur.fetchall():
            self.editStatus.addItem(n, i)

        conn.close()

    def load_drakor(self):
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT d.id_drakor, d.judul, g.nama_genre,
                   d.episode_terakhir, d.total_episode,
                   s.nama_status, d.favorit, poster_path
            FROM drakor d
            LEFT JOIN genre g ON d.id_genre=g.id_genre
            LEFT JOIN status s ON d.id_status=s.id_status
            WHERE d.id_user=?
        """, (self.id_user,))

        data = cur.fetchall()
        print("=== DEBUG DRAKOR DATA ===")
        for row in data:
            print(row)
        print("========================")

        conn.close()

        self.list.clear()

        for d in data:
            id_drakor = d[0]
            judul = d[1]
            genre = d[2] or "-"
            episode = f"{d[3]}/{d[4]}"
            status = d[5] or "-"
            favorit = d[6]
            poster_path = d[7]

            pixmap = None
            if poster_path:
                base = os.path.abspath(os.path.dirname(__file__))
                full_path = os.path.abspath(os.path.join(base, poster_path.replace("\\", "/")))

                print("Mengecek poster:", full_path, "exists:", os.path.exists(full_path))

                if os.path.exists(full_path):
                    pixmap = QPixmap(full_path)
                    


            item = QListWidgetItem()
            item.setSizeHint(QSize(100, 120))
            item.setData(Qt.UserRole, id_drakor)

            widget = DrakorItem(judul, genre, episode, status, favorit, pixmap)

            self.list.addItem(item)
            self.list.setItemWidget(item, widget)

    # ================= SELECT ROW =================
    def select_row(self):
        item = self.list.currentItem()
        if not item:
            return

        self.selected_id = item.data(Qt.UserRole)

        # Ambil data dari database supaya tidak error
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT judul, id_genre, id_status, episode_terakhir, total_episode, favorit
            FROM drakor
            WHERE id_drakor=?
        """, (self.selected_id,))
        data = cur.fetchone()
        conn.close()
    
        judul, id_genre, id_status, ep_now, ep_total, fav = data

        self.editJudul.setText(judul)
        self.editTotal.setValue(ep_total)
        self.editEpisode.setMaximum(ep_total)
        self.editEpisode.setValue(ep_now)
        self.editFavorit.setChecked(bool(fav))

        # Set genre
        for i in range(self.editGenre.count()):
            if self.editGenre.itemData(i) == id_genre:
                self.editGenre.setCurrentIndex(i)
                break

        # Set status
        for i in range(self.editStatus.count()):
            if self.editStatus.itemData(i) == id_status:
                self.editStatus.setCurrentIndex(i)
                break

    # ================= UPDATE DRAKOR =================        
    def update_drakor(self):
        if not self.selected_id:
            QMessageBox.warning(self, "Edit", "Pilih data dulu")
            return
        
        ep_now = self.editEpisode.value()
        ep_total = self.editTotal.value()

        if ep_now > ep_total:
            QMessageBox.warning(
                self,
                "Validasi Episode",
                "Episode terakhir tidak boleh lebih besar dari total episode",
                "Silahkan Diperbaiki"
            )

        #Status otomatis
        if ep_now == 0:
            status_name = "Akan Ditonton"
        elif ep_now == ep_total:
            status_name = "Selesai"
            ep_now = ep_total
        else:
            status_name = "Sedang Ditonton"

        status_id = None
        for i in range(self.editStatus.count()):
            if self.editStatus.itemText(i) == status_name:
                status_id = self.editStatus.itemData(i)
                self.editStatus.setCurrentIndex(i)
                break

        conn = connect_db()
        cur = conn.cursor()

        cur.execute("""
            UPDATE drakor SET
                judul=?,
                total_episode=?,
                episode_terakhir=?,
                id_genre=?,
                id_status=?,
                favorit=?
            WHERE id_drakor=?
            """, (
                self.editJudul.text(),
                ep_total,
                ep_now,
                self.editGenre.currentData(),
                status_id,
                1 if self.editFavorit.isChecked() else 0,
                self.selected_id
            ))

        conn.commit()
        conn.close()
    
        QMessageBox.information(self, "Sukses", "Data berhasil diupdate")
        self.load_drakor()


    def hapus_drakor(self):
        if not self.selected_id:
            QMessageBox.warning(self, "Hapus", "Pilih data dulu")
            return

        conn = connect_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM drakor WHERE id_drakor=?", (self.selected_id,))
        conn.commit()
        conn.close()

        self.load_drakor()
        self.selected_id = None

    def reset_drakor(self):
        reply = QMessageBox.question(
            self, "Reset", "Hapus semua data?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("DELETE FROM drakor WHERE id_user=?", (self.id_user,))
            conn.commit()
            conn.close()
            self.load_drakor()

    def search_drakor(self, text):
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT d.id_drakor, d.judul, g.nama_genre,
                   d.episode_terakhir, d.total_episode,
                   s.nama_status, d.favorit, d.poster_path
            FROM drakor d
            LEFT JOIN genre g ON d.id_genre=g.id_genre
            LEFT JOIN status s ON d.id_status=s.id_status
            WHERE d.judul LIKE ? AND d.id_user=?
        """, (f"%{text}%", self.id_user))
        data = cur.fetchall()
        conn.close()

        #Bersihkan list
        self.list.clear()

        #Jika tidak ada hasil
        if not data:
            return

        for d in data:
            id_drakor = d[0]
            judul = d[1]
            genre = d[2] or "-"
            episode = f"{d[3]}/{d[4]}"
            status = d[5] or "-"
            favorit = d[6]
            poster_path = d[7]

        # === POSTER ===
        pixmap = None
        if poster_path:
            base = os.path.abspath(os.path.dirname(__file__))
            full_path = os.path.abspath(
                os.path.join(base, poster_path.replace("\\", "/"))
            )
            if os.path.exists(full_path):
                pixmap = QPixmap(full_path)

        # === ITEM BARU ===
        item = QListWidgetItem()
        item.setSizeHint(QSize(100, 120))
        item.setData(Qt.UserRole, id_drakor)

        widget = DrakorItem(judul, genre, episode, status, favorit, pixmap)

        self.list.addItem(item)
        self.list.setItemWidget(item, widget)


# ================= RUN =================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = WelcomeWindow()
    w.show()
    sys.exit(app.exec())