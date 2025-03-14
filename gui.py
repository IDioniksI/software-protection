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
        self.password_widget, self.password_input, self.toggle_password_button = create_password_widget()

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

        layout = QVBoxLayout()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_combo)
        # layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_widget)
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
        self.password_widget, self.password_input, self.toggle_password_button = create_password_widget()

        self.create_button = QPushButton("Створити")
        self.create_button.clicked.connect(self.create_user)

        layout = QVBoxLayout()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_widget)
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

        if not checking_password(password):
            QMessageBox.warning(self, "Помилка", "Пароль має містити латинські букви, кирилицю та цифри")
            return

        self.db.create_user(username, password)
        QMessageBox.information(self, "Успіх", f"Новий користувач {username} створений")
        self.accept()


class MainApp(QMainWindow):
    def __init__(self, username, db):
        super().__init__()
        self.resize(300, 200)
        self.db = db
        self.username = username

        role = self.db.get_user_role(username)
        if role == "admin":
            self.setWindowTitle("Головне вікно (адміністратор)")
        else:
            self.setWindowTitle("Головне вікно")

        self.change_password = QPushButton("Змінити пароль")
        self.change_password.clicked.connect(self.password_change)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        layout.addWidget(self.change_password)

    def password_change(self):
        dialog = ChangePasswordDialog(self.username, self.db)
        dialog.exec()


class ChangePasswordDialog(QDialog):
    def __init__(self, username, db):
        super().__init__()
        self.resize(300, 200)
        self.db = db
        self.username = username

        self.setWindowTitle(f"Зміна пароля для {username}")

        self.password_label = QLabel("Старий пароль:")
        self.password_widget, self.password_input, self.toggle_password_button = create_password_widget()

        self.new_password_label = QLabel("Новий пароль:")
        self.new_password_widget, self.new_password_input, self.toggle_new_password_button = create_password_widget()

        self.repeat_new_password_label = QLabel("Повторіть новий пароль:")
        self.repeat_new_password_widget, self.repeat_new_password_input, self.toggle_repeat_new_password_button = create_password_widget()

        self.change_button = QPushButton("Змінити")
        self.change_button.clicked.connect(self.change_password)

        layout = QVBoxLayout()
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_widget)
        layout.addWidget(self.new_password_label)
        layout.addWidget(self.new_password_widget)
        layout.addWidget(self.repeat_new_password_label)
        layout.addWidget(self.repeat_new_password_widget)
        layout.addWidget(self.change_button)

        self.setLayout(layout)

    def change_password(self):
        old_password = self.password_input.text()
        new_password = self.new_password_input.text()
        repeat_new_password = self.repeat_new_password_input.text()

        if not self.db.get_user(self.username, old_password):
            QMessageBox.warning(self, "Помилка", "Невірний старий пароль")
            return

        if new_password != repeat_new_password:
            QMessageBox.warning(self, "Помилка", "Новий пароль не співпадає")
            return

        self.db.change_password(self.username, new_password)
        QMessageBox.information(self, "Успіх", "Пароль змінено")
        self.accept()


def checking_password(password):
    has_latin = re.search(r'[A-Za-z]', password) is not None
    has_cyrillic = re.search(r'[А-Яа-яЁёЇїІіЄєҐґ]', password) is not None
    has_digit = re.search(r'\d', password) is not None

    return has_latin and has_cyrillic and has_digit

def toggle_password_visibility(password_input: QLineEdit, toggle_password_button: QPushButton):
    if toggle_password_button.isChecked():
        password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        toggle_password_button.setText("🙈")
    else:
        password_input.setEchoMode(QLineEdit.EchoMode.Password)
        toggle_password_button.setText("👁️")

def create_password_widget():
    line_edit = QLineEdit()
    line_edit.setEchoMode(QLineEdit.EchoMode.Password)

    button = QPushButton("👁️")
    button.setCheckable(True)
    button.setFixedSize(30, 25)
    button.clicked.connect(lambda: toggle_password_visibility(line_edit, button))

    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(line_edit)
    layout.addWidget(button)

    return widget, line_edit, button



if __name__ == "__main__":
    app = QApplication(sys.argv)

    login_dialog = LoginDialog()
    if login_dialog.exec() == QDialog.DialogCode.Accepted:
        main_window = MainApp(login_dialog.selected_user, login_dialog.db)
        main_window.show()
        sys.exit(app.exec())