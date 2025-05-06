import sqlite3
import bcrypt
import os

class UsersDB:
    def __init__(self, connection=None):
        self.connection = connection or sqlite3.connect(":memory:")
        self.cursor = self.connection.cursor()
        self.create_tables()
        self.create_admin_user()

    def create_tables(self):
        with self.connection:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    login TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    password_restriction INTEGER DEFAULT 1,
                    block INTEGER DEFAULT 0,
                    first_ent INTEGER DEFAULT 1
                )
            """)

    def hash_password(self, password: str) -> str:
        if password == "":
            return ""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)
        return hashed.decode()

    def check_password(self, password: str, stored_password: str) -> bool:
        if stored_password == "":
            return password == ""
        return bcrypt.checkpw(password.encode(), stored_password.encode())

    def create_admin_user(self):
        with self.connection:
            self.cursor.execute("""
                INSERT OR IGNORE INTO users (login, password, role, password_restriction, block, first_ent)
                VALUES ('ADMIN', '', 'admin', 0, 0, 1)
            """)

    def get_user(self, login, password):
        with self.connection:
            self.cursor.execute("SELECT * FROM users WHERE login = ?", (login,))
            user = self.cursor.fetchone()
            if user and self.check_password(password, user[2]):
                return user
        return None

    def get_user_role(self, login):
        with self.connection:
            self.cursor.execute("SELECT role FROM users WHERE login = ?", (login,))
            return self.cursor.fetchone()[0]

    def get_all_logins(self):
        with self.connection:
            self.cursor.execute("SELECT login FROM users")
            return [row[0] for row in self.cursor.fetchall()]

    def create_user(self, login, password, role='user', password_restriction=1, block=0, first_ent=1):
        hashed_password = self.hash_password(password)
        with self.connection:
            self.cursor.execute("INSERT INTO users (login, password, role, password_restriction, block, first_ent) "
                                "VALUES (?, ?, ?, ?, ?, ?)", (login, hashed_password, role, password_restriction, block, first_ent))

    def check_login(self, login):
        with self.connection:
            self.cursor.execute("SELECT 1 FROM users WHERE login = ?", (login,))
            return self.cursor.fetchone() is not None

    def change_password(self, login, new_password):
        hashed_password = self.hash_password(new_password)
        with self.connection:
            self.cursor.execute("UPDATE users SET password = ? WHERE login = ?", (hashed_password, login))

    def get_password_restriction(self, login):
        with self.connection:
            self.cursor.execute("SELECT password_restriction FROM users WHERE login = ?", (login,))
            return self.cursor.fetchone()[0]

    def get_all_users(self):
        with self.connection:
            self.cursor.execute("SELECT * FROM users")
            return self.cursor.fetchall()

    def change_role(self, login, role):
        with self.connection:
            self.cursor.execute("UPDATE users SET role = ? WHERE login = ?", (role, login))

    def change_block(self, login, block):
        with self.connection:
            self.cursor.execute("UPDATE users SET block = ? WHERE login = ?", (block, login))

    def change_password_restriction(self, login, password_restriction):
        with self.connection:
            self.cursor.execute("UPDATE users SET password_restriction = ? WHERE login = ?", (password_restriction, login))

    def get_first_ent(self, login):
        with self.connection:
            self.cursor.execute("SELECT first_ent FROM users WHERE login = ?", (login,))
            return self.cursor.fetchone()[0]

    def change_first_ent(self, login, first_ent):
        with self.connection:
            self.cursor.execute("UPDATE users SET first_ent = ? WHERE login = ?", (first_ent, login))

    def get_block(self, login):
        with self.connection:
            self.cursor.execute("SELECT block FROM users WHERE login = ?", (login,))
            return self.cursor.fetchone()[0]


def load_to_memory_from_file(file_db_path: str) -> sqlite3.Connection:
    file_conn = sqlite3.connect(file_db_path)
    mem_conn = sqlite3.connect(":memory:")
    file_conn.backup(mem_conn)
    file_conn.close()
    os.remove(file_db_path)
    return mem_conn


def save_connection_to_bytes(conn: sqlite3.Connection) -> bytes:
    temp_file = "temp.db"
    disk_conn = sqlite3.connect(temp_file)
    conn.backup(disk_conn)
    disk_conn.close()
    with open(temp_file, "rb") as f:
        data = f.read()
    os.remove(temp_file)
    return data


def load_bytes_to_connection(data: bytes) -> sqlite3.Connection:
    if not data.startswith(b'SQLite format 3\x00'):
        raise ValueError("Файл не є SQLite-базою")

    temp_file = "temp_decrypted.db"
    with open(temp_file, "wb") as f:
        f.write(data)
    mem_conn = sqlite3.connect(":memory:")
    disk_conn = sqlite3.connect(temp_file)
    disk_conn.backup(mem_conn)
    disk_conn.close()
    os.remove(temp_file)
    return mem_conn


if __name__ == '__main__':
    db = UsersDB()
    print("Database created")