import sqlite3

class UsersDB:
    def __init__(self):
        self.connection = sqlite3.connect("users.db")
        self.cursor = self.connection.cursor()
        self.create_tables()
        self.create_admin_user()

    def create_tables(self):
        with self.connection:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    login TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT DEFAULT 'user'
                )
            """)

    def create_admin_user(self):
        with self.connection:
            self.cursor.execute("""
                INSERT OR IGNORE INTO users (login, password, role)
                VALUES ('ADMIN', 'admin', 'admin')
            """)

    def get_user(self, login, password):
        with self.connection:
            self.cursor.execute("SELECT * FROM users WHERE login = ? AND password = ?", (login, password))
            return self.cursor.fetchone()

    def get_all_logins(self):
        """Отримати список всіх логінів з бази даних."""
        with self.connection:
            self.cursor.execute("SELECT login FROM users")
            return [row[0] for row in self.cursor.fetchall()]

    def create_user(self, login, password, role='user'):
        with self.connection:
            self.cursor.execute("INSERT INTO users (login, password, role) VALUES (?, ?, ?)", (login, password, role))

    def check_login(self, login):
        with self.connection:
            self.cursor.execute("SELECT 1 FROM users WHERE login = ?", (login,))
            return self.cursor.fetchone() is not None


if __name__ == '__main__':
    db = UsersDB()
    print("Database created")