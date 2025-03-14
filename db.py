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
                    role TEXT DEFAULT 'user'
                )
            """),
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS limitation (
                    id INTEGER PRIMARY KEY,
                    profile_id INTEGER NOT NULL,
                    block TEXT NOT NULL,
                    password_restriction TEXT NOT NULL,
                    FOREIGN KEY (profile_id) REFERENCES users(id)
                )
            """)

    def create_admin_user(self):
        with self.connection:
            self.cursor.execute("""
                INSERT OR IGNORE INTO users (login, password, role)
                VALUES ('ADMIN', '', 'admin')
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

    def create_user(self, login, password, role='user'):
        with self.connection:
            self.cursor.execute("INSERT INTO users (login, password, role) VALUES (?, ?, ?)", (login, password, role))

    def check_login(self, login):
        with self.connection:
            self.cursor.execute("SELECT 1 FROM users WHERE login = ?", (login,))
            return self.cursor.fetchone() is not None

    def change_password(self, login, new_password):
        with self.connection:
            self.cursor.execute("UPDATE users SET password = ? WHERE login = ?", (new_password, login))



if __name__ == '__main__':
    db = UsersDB()
    print("Database created")