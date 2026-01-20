import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "drakor.db")

def connect_db():
    return sqlite3.connect(DB_PATH)

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    # Tabel User
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user (
        id_user INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """) 


    # Tabel Genre
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS genre (
        id_genre INTEGER PRIMARY KEY AUTOINCREMENT,
        nama_genre TEXT NOT NULL UNIQUE
    )
    """)

    # Tabel Status
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS status (
        id_status INTEGER PRIMARY KEY AUTOINCREMENT,
        nama_status TEXT NOT NULL UNIQUE
    )
    """)

    # Tabel Drakor
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS drakor (
        id_drakor INTEGER PRIMARY KEY AUTOINCREMENT,
        judul TEXT NOT NULL,
        total_episode INTEGER,
        episode_terakhir INTEGER,
        favorit INTEGER DEFAULT 0,
        id_genre INTEGER,
        id_status INTEGER,
        id_user INTEGER,
        poster_path Text,
        FOREIGN KEY (id_genre) REFERENCES genre(id_genre),
        FOREIGN KEY (id_status) REFERENCES status(id_status),
        FOREIGN KEY (id_user) REFERENCES user(id_user)
    )
    """)

    #Peringatan Admin
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS peringatan_admin (
        id_warning INTEGER PRIMARY KEY AUTOINCREMENT,
        id_user INTEGER,
        pesan TEXT,
        tanggal TEXT,
        FOREIGN KEY (id_user) REFERENCES user(id_user)
    )
    """)

    conn.commit()
    conn.close()
   

def insert_default_data():
    conn = connect_db()
    cursor = conn.cursor()

    genre_default = [
        ("Romance",),
        ("Action",),
        ("Comedy",),
        ("Fantasy",),
        ("Thriller",)
    ]

    status_default = [
        ("Akan Ditonton",),
        ("Sedang Ditonton",),
        ("Selesai",)
    ]

    user_default = [
    ("admin", "123", "admin"),
    ("user1", "123", "user"),
    ("user2", "123", "user")
]

    cursor.executemany(
        "INSERT OR IGNORE INTO genre (nama_genre) VALUES (?)",
        genre_default
    )

    cursor.executemany(
        "INSERT OR IGNORE INTO status (nama_status) VALUES (?)",
        status_default
    )

    cursor.executemany("""
    INSERT OR IGNORE INTO user (username, password, role)
    VALUES (?, ?, ?)
        """, user_default)

    conn.commit()
    conn.close()
