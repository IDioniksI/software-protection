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
                    id INTEGER PRIMARY KEY,
                    login TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    password_restriction INTEGER DEFAULT 1,
                    block INTEGER DEFAULT 0
                )
            """)

    def create_admin_user(self):
        with self.connection:
            self.cursor.execute("""
                INSERT OR IGNORE INTO users (login, password, role, password_restriction, block)
                VALUES ('ADMIN', '', 'admin', 0, 0)
            """)

    def get_user(self, login, password):
        with self.connection:
            self.cursor.execute("SELECT * FROM users WHERE login = ? AND password = ?", (login, password))
            return self.cursor.fetchone()

    def get_user_role(self, login):
        with self.connection:
            self.cursor.execute("SELECT role FROM users WHERE login = ?", (login,))
            return self.cursor.fetchone()[0]

    def get_all_logins(self):
        with self.connection:
            self.cursor.execute("SELECT login FROM users")
            return [row[0] for row in self.cursor.fetchall()]

    def create_user(self, login, password, role='user', password_restriction=1, block=0):
        with self.connection:
            self.cursor.execute("INSERT INTO users (login, password, role, password_restriction, block) "
                                "VALUES (?, ?, ?, ?, ?)", (login, password, role, password_restriction, block))

    def check_login(self, login):
        with self.connection:
            self.cursor.execute("SELECT 1 FROM users WHERE login = ?", (login,))
            return self.cursor.fetchone() is not None

    def change_password(self, login, new_password):
        with self.connection:
            self.cursor.execute("UPDATE users SET password = ? WHERE login = ?", (new_password, login))

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


if __name__ == '__main__':
    db = UsersDB()
    print("Database created")