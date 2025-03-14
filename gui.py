from PyQt6.QtWidgets import (QApplication, QMainWindow, QListWidget, QTextEdit, QHBoxLayout, QVBoxLayout, QLabel,
                             QWidget, QPushButton, QDialog, QLineEdit, QMessageBox, QMenu, QInputDialog,
                             QScrollArea, QComboBox, QFileDialog, QDateEdit, QTableWidgetItem, QTableWidget,
                             QCheckBox, QDateTimeEdit, QDialogButtonBox, QGridLayout, QFrame)

from PyQt6.QtCore import Qt, QDate, QByteArray, QDateTime
from PyQt6.QtGui import QPixmap, QFont
from db import UsersDB
import sys
import re


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вхід")
        self.resize(250, 150)
        self.db = UsersDB()
        self.selected_user = None
        self.attempts = 0

        self.username_label = QLabel("Логін:")
        self.username_combo = QComboBox()
        self.username_combo.addItems(self.db.get_all_logins())
        # self.username_input = QLineEdit()


        self.password_label = QLabel("Пароль:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.toggle_password_button = QPushButton("👁️")
        self.toggle_password_button.setCheckable(True)
        self.toggle_password_button.setFixedSize(30, 25)
        self.toggle_password_button.clicked.connect(
            lambda: toggle_password_visibility(self.password_input, self.toggle_password_button))

        self.login_button = QPushButton("Увійти")
        self.login_button.clicked.connect(self.check_login)

        self.create_user = QPushButton("Створити користувача")
        self.create_user.clicked.connect(self.create_new_user)

        self.create_user.setStyleSheet("""
            QPushButton {
                background-color: transparent;  /* Прозорий фон */
                color: #2271bf;  /* Синій текст */
                border: none;  /* Без рамки */
            }
            QPushButton:hover {
                text-decoration: underline;  /* Підкреслення при наведенні */
                color: #3399FF;
            }
        """)

        password_widget = QWidget()
        password_layout = QHBoxLayout(password_widget)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.toggle_password_button)

        layout = QVBoxLayout()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_combo)
        # layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(password_widget)
        layout.addWidget(self.login_button)
        layout.addWidget(self.create_user)

        self.setLayout(layout)

    def check_login(self):
        # username = self.username_input.text()
        username = self.username_combo.currentText()
        password = self.password_input.text()

        user = self.db.get_user(username, password)
        if user:
            self.selected_user = username
            self.accept()
        else:
            self.attempts += 1
            if self.attempts >= 3:
                QMessageBox.critical(self, "Помилка", "Ви вичерпали всі спроби")
                self.reject()
            else:
                QMessageBox.warning(self, "Помилка", f"Невірний логін або пароль, у вас залишилося "
                                                     f"{3 - self.attempts} спроб")

    def create_new_user(self):
        dialog = CreateNewUserDialog(self.db)
        if dialog.exec():
            self.username_combo.clear()
            self.username_combo.addItems(self.db.get_all_logins())
        else:
            QMessageBox.information(self, "Увага", "Користувача не створено")

class CreateNewUserDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db

        self.setWindowTitle("Створення користувача")

        self.username_label = QLabel("Логін:")
        self.username_input = QLineEdit()

        self.password_label = QLabel("Пароль:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.toggle_password_button = QPushButton("👁️")
        self.toggle_password_button.setCheckable(True)
        self.toggle_password_button.setFixedSize(30, 25)
        self.toggle_password_button.clicked.connect(
            lambda: toggle_password_visibility(self.password_input, self.toggle_password_button))

        self.create_button = QPushButton("Створити")
        self.create_button.clicked.connect(self.create_user)

        password_widget = QWidget()
        password_layout = QHBoxLayout(password_widget)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.toggle_password_button)

        layout = QVBoxLayout()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(password_widget)
        layout.addWidget(self.create_button)

        self.setLayout(layout)

    def create_user(self):
        # 6. Наявність латинських букв, символів кирилиці та цифр.
        username = self.username_input.text()
        password = self.password_input.text()

        if self.db.check_login(username):
            QMessageBox.warning(self, "Помилка", f"Користувач з логіном {username} вже існує")
            return

        if not username or not password:
            QMessageBox.warning(self, "Помилка", "Логін та пароль не можуть бути пустими")
            return

        if not self.checking_password(password):
            QMessageBox.warning(self, "Помилка", "Пароль має містити латинські букви, кирилицю та цифри")
            return

        self.db.create_user(username, password)
        QMessageBox.information(self, "Успіх", f"Новий користувач {username} створений")
        self.accept()


    def checking_password(self, password):
        has_latin = re.search(r'[A-Za-z]', password) is not None
        has_cyrillic = re.search(r'[А-Яа-яЁёЇїІіЄєҐґ]', password) is not None
        has_digit = re.search(r'\d', password) is not None

        return has_latin and has_cyrillic and has_digit


class MainApp(QMainWindow):
    def __init__(self, username, db):
        super().__init__()
        self.db = db

        self.setWindowTitle("Головне вікно")
        self.setGeometry(100, 100, 600, 400)
        label = QLabel(f"{username},  Вітаємо у програмі!", self)
        label.setGeometry(200, 150, 200, 50)


def toggle_password_visibility(password_input: QLineEdit, toggle_password_button: QPushButton):
    if toggle_password_button.isChecked():
        password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        toggle_password_button.setText("🙈")
    else:
        password_input.setEchoMode(QLineEdit.EchoMode.Password)
        toggle_password_button.setText("👁️")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    login_dialog = LoginDialog()
    if login_dialog.exec() == QDialog.DialogCode.Accepted:
        main_window = MainApp(login_dialog.selected_user, login_dialog.db)
        main_window.show()
        sys.exit(app.exec())