from PyQt6.QtWidgets import (QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QLabel, QWidget, QPushButton,
                             QDialog, QLineEdit, QMessageBox, QComboBox, QTableWidgetItem, QTableWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QAction

from installer.functions.get_info import get_information
from installer.functions.registry import load_from_registry, verify_signature, hash_data
from db import UsersDB

import sys
import re
import os


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
            if self.db.get_block(username) == 1:
                QMessageBox.warning(self, "Помилка", f"Аккаунт {username} заблоковано, оберіть інший")
                return
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
    def __init__(self, db, admin=False):
        super().__init__()
        self.db = db

        self.setWindowTitle("Створення користувача")

        self.username_label = QLabel("Логін:")
        self.username_input = QLineEdit()

        self.password_label = QLabel("Пароль:")
        self.password_widget, self.password_input, self.toggle_password_button = create_password_widget()

        layout = QVBoxLayout()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_widget)

        if admin == True:
            self.password_restriction_label = QLabel("Обмеження паролю:")
            self.password_restriction = QComboBox()
            self.password_restriction.addItems(["Так", "Ні"])
            layout.addWidget(self.password_restriction_label)
            layout.addWidget(self.password_restriction)

            self.create_button = QPushButton("Створити")
            self.create_button.clicked.connect(self.create_user_for_admin)
        else:
            self.create_button = QPushButton("Створити")
            self.create_button.clicked.connect(self.create_user)


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

    def create_user_for_admin(self):
        username = self.username_input.text()
        password = self.password_input.text()
        password_restriction = self.password_restriction.currentText()

        if password_restriction == "Так":
            password_restriction = 1
            if not checking_password(password):
                QMessageBox.warning(self, "Помилка", "Пароль має містити латинські букви, кирилицю та цифри")
                return
        else:
            password_restriction = 0

        if self.db.check_login(username):
            QMessageBox.warning(self, "Помилка", f"Користувач з логіном {username} вже існує")
            return

        if not username:
            QMessageBox.warning(self, "Помилка", "Логін не може бути пустими")
            return

        self.db.create_user(username, password, password_restriction=password_restriction)
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
            banner = QLabel()
            banner.setPixmap(QPixmap(get_resource_path("raccoon.jpg")))
            banner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            self.setWindowTitle("Головне вікно")
            banner = QLabel()
            banner.setPixmap(QPixmap(get_resource_path("raccoon_simple.jpg")))
            banner.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.change_password = QPushButton("Змінити пароль")
        self.change_password.clicked.connect(self.password_change)

        self.users_table = QPushButton("Список користувачів")
        self.users_table.clicked.connect(self.show_users_table)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        menu_bar = self.menuBar()

        menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: #d1cfcf;
                border-top: 1px solid black;
                border-bottom: 1px solid black;
            }
            QMenuBar::item:selected {
                background-color: #9c9898;
            }
            QMenu {
                background-color: #d1cfcf;
                border: 1px solid black;
            }
            QMenu::item:selected {
                background-color: #9c9898;
            }
        """)

        file_menu = menu_bar.addMenu("Довідка")
        about_program = QAction("Про програму", self)
        about_program.triggered.connect(self.about_program_dialog)
        file_menu.addAction(about_program)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        layout.addWidget(banner)
        layout.addWidget(self.change_password)
        if role == "admin":
            layout.addWidget(self.users_table)

        if self.db.get_first_ent(self.username) == 1:
            self.show()
            self.db.change_first_ent(self.username, 0)
            self.window_first_ent()

    def about_program_dialog(self):
        QMessageBox.information(self, "Про програму", "Автор програми: студент ФБ-25 Кравченко Максим "
                                                      "\nІндивідуальне завдання: 6. Наявність латинських букв, символів кирилиці та цифр.")

    def password_change(self):
        dialog = ChangePasswordDialog(self.username, self.db)
        dialog.exec()

    def show_users_table(self):
        dialog = UsersTableDialog(self.db, self.username)
        dialog.exec()

    def window_first_ent(self):
        dialog = FirstEntDialog(self.username, self.db)
        dialog.exec()

class FirstEntDialog(QDialog):
    def __init__(self, username, db):
        super().__init__()
        self.resize(300, 200)
        self.db = db
        self.username = username

        self.setWindowTitle(f"Перший вхід для {username}")

        self.first_ent_label = QLabel("Ви вперше ввійшли після створення аккаунту, або після зміни обмеження паролю")
        self.first_ent_label_2 = QLabel("Оберіть нижче дію, яку ви хочете виконати:")

        self.change_password = QPushButton("Змінити пароль")
        self.change_password.clicked.connect(self.password_change)

        self.quit_button = QPushButton("Закрити програму")
        self.quit_button.clicked.connect(self.quit_app)

        self.continue_button = QPushButton("Продовжити без змін")
        self.continue_button.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(self.first_ent_label)
        layout.addWidget(self.first_ent_label_2)
        layout.addWidget(self.change_password)
        layout.addWidget(self.quit_button)
        layout.addWidget(self.continue_button)

        self.setLayout(layout)

    def password_change(self):
        dialog = ChangePasswordDialog(self.username, self.db)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            self.accept()

    def quit_app(self):
        QApplication.instance().quit()
        sys.exit(0)


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

        if self.db.get_password_restriction(self.username) == 1:
            if not checking_password(new_password):
                QMessageBox.warning(self, "Помилка", "Пароль має містити латинські букви, кирилицю та цифри")
                return

        self.db.change_password(self.username, new_password)
        QMessageBox.information(self, "Успіх", "Пароль змінено")
        self.accept()

class UsersTableDialog(QDialog):
    def __init__(self, db, own_username):
        super().__init__()
        self.db = db
        self.own_username = own_username
        self.setWindowTitle("Список користувачів")
        self.resize(490, 300)

        self.users_table = QTableWidget()
        self.users_table.setColumnCount(4)
        self.users_table.setHorizontalHeaderLabels(["Логін", "Роль", "Обмеження паролю", "Статус"])
        self.users_table.setColumnWidth(2, 150)
        self.users_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.users_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.users_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.users_table.doubleClicked.connect(self.change_user_role)

        self.fill_table()

        self.change_role_button = QPushButton("Змінити роль")
        self.change_role_button.clicked.connect(self.change_user_role)

        self.add_unique_user = QPushButton("Додати унікального користувача")
        self.add_unique_user.clicked.connect(self.add_uni_user)

        self.block_user = QPushButton("Заблокувати/розблокувати користувача")
        self.block_user.clicked.connect(self.block_unblock_user)

        self.change_password_restriction = QPushButton("Змінити обмеження паролю")
        self.change_password_restriction.clicked.connect(self.change_password_restriction_func)

        widget_1 = QWidget()
        layout_1 = QHBoxLayout(widget_1)
        layout_1.setContentsMargins(0, 0, 0, 0)
        layout_1.addWidget(self.change_role_button)
        layout_1.addWidget(self.change_password_restriction)

        widget_2 = QWidget()
        layout_2 = QHBoxLayout(widget_2)
        layout_2.setContentsMargins(0, 0, 0, 0)
        layout_2.addWidget(self.add_unique_user)
        layout_2.addWidget(self.block_user)


        layout = QVBoxLayout()
        layout.addWidget(self.users_table)
        layout.addWidget(widget_1)
        layout.addWidget(widget_2)

        # layout.addWidget(self.change_role_button)
        # layout.addWidget(self.add_unique_user)
        # layout.addWidget(self.block_user)
        # layout.addWidget(self.change_password_restriction)

        self.setLayout(layout)

    def fill_table(self):
        self.users_table.setRowCount(0)
        for user in self.db.get_all_users():
            row_position = self.users_table.rowCount()
            self.users_table.insertRow(row_position)
            self.users_table.setItem(row_position, 0, QTableWidgetItem(user[1]))
            if user[3] == "admin":
                self.users_table.setItem(row_position, 1, QTableWidgetItem("Адміністратор"))
            else:
                self.users_table.setItem(row_position, 1, QTableWidgetItem("Користувач"))

            if user[4] == 1:
                self.users_table.setItem(row_position, 2, QTableWidgetItem("Так"))
            else:
                self.users_table.setItem(row_position, 2, QTableWidgetItem("Ні"))

            if user[5] == 1:
                self.users_table.setItem(row_position, 3, QTableWidgetItem("Заблокований"))
            else:
                self.users_table.setItem(row_position, 3, QTableWidgetItem("Активний"))


    def change_user_role(self):
        selected_row = self.users_table.currentRow()

        if selected_row == -1:
            QMessageBox.warning(self, "Помилка", "Виділіть користувача")
            return

        login = self.users_table.item(selected_row, 0).text()

        if login == self.own_username:
            QMessageBox.warning(self, "Помилка", "Неможливо понизити собі роль")
            return

        dialog = ChangeUserRoleDialog(self.db, login)
        dialog.exec()
        self.fill_table()

    def add_uni_user(self):
        dialog = CreateNewUserDialog(self.db, admin=True)
        if dialog.exec():
            self.fill_table()
        else:
            QMessageBox.information(self, "Увага", "Користувача не створено")

    def block_unblock_user(self):
        selected_row = self.users_table.currentRow()

        if selected_row == -1:
            QMessageBox.warning(self, "Помилка", "Виділіть користувача")
            return

        login = self.users_table.item(selected_row, 0).text()
        block = self.users_table.item(selected_row, 3).text()

        if login == self.own_username:
            QMessageBox.warning(self, "Помилка", "Неможливо заблокувати себе")
            return

        if block == "Заблокований":
            self.db.change_block(login, 0)
            QMessageBox.information(self, "Успіх", f"Користувач {login} розблокований")
        else:
            self.db.change_block(login, 1)
            QMessageBox.information(self, "Успіх", f"Користувач {login} заблокований")

        self.fill_table()

    def change_password_restriction_func(self):
        selected_row = self.users_table.currentRow()

        if selected_row == -1:
            QMessageBox.warning(self, "Помилка", "Виділіть користувача")
            return

        login = self.users_table.item(selected_row, 0).text()
        password_restriction = self.users_table.item(selected_row, 2).text()

        if password_restriction == "Так":
            self.db.change_password_restriction(login, 0)
            QMessageBox.information(self, "Успіх", f"Обмеження паролю для {login} відключено")
        else:
            self.db.change_password_restriction(login, 1)
            if self.db.get_first_ent(login) == 0:
                self.db.change_first_ent(login, 1)
            QMessageBox.information(self, "Успіх", f"Обмеження паролю для {login} включено")

        self.fill_table()


class ChangeUserRoleDialog(QDialog):
    def __init__(self, db, login):
        super().__init__()
        self.login = login
        self.db = db
        self.setWindowTitle("Зміна ролі")

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Змінити роль для {login}"))

        self.choose_role = QComboBox(self)
        self.choose_role.addItems(["Адміністратор", "Користувач"])
        layout.addWidget(self.choose_role)

        self.change_button = QPushButton("Змінити")
        self.change_button.clicked.connect(self.change_role)
        layout.addWidget(self.change_button)

    def change_role(self):
        role_cyrillic = self.choose_role.currentText()
        if role_cyrillic == "Адміністратор":
            role = "admin"
        else:
            role = "user"

        self.db.change_role(self.login, role)

        QMessageBox.information(self, "Успіх", f"Роль змінена на {role_cyrillic}")
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

def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    all_info = get_information(os.path.splitdrive(os.getcwd())[0] + r'\\')
    hashed_info = hash_data(all_info)

    public_key_pem = load_from_registry(parameter='PublicKey')

    if not public_key_pem:
        QMessageBox.warning(None, 'Помилка', 'Відсутні записи програми в реєстрі \nПеревстановіть програму')
        sys.exit(0)

    if not verify_signature(public_key_pem, hashed_info):
        QMessageBox.warning(None, 'Помилка', 'Інформація про систему була змінена \nПрограма закривається')
        sys.exit(0)

    login_dialog = LoginDialog()
    if login_dialog.exec() == QDialog.DialogCode.Accepted:
        main_window = MainApp(login_dialog.selected_user, login_dialog.db)
        main_window.show()
        sys.exit(app.exec())