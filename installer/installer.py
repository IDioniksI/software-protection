from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QLabel, QWidget, QPushButton, QLineEdit,
                             QMessageBox, QFileDialog, QProgressBar, QStackedWidget)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap

from functions.get_info import get_information
from functions.registry import keys_generation_data_signing

import time as t

import os
import sys
import shutil


reg_path = r"SOFTWARE\Kravchenko"


class Installer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Інсталятор My Security Program")
        self.resize(400, 250)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.page_select_path = self.select_path_page()
        self.page_progress = self.create_progress_page()
        self.page_finish = self.finish_installation()

        self.stacked_widget.addWidget(self.page_select_path)
        self.stacked_widget.addWidget(self.page_progress)
        self.stacked_widget.addWidget(self.page_finish)

    def select_path_page(self):
        page = QWidget()
        layout = QVBoxLayout()

        self.path_to_install = QLabel("Оберіть шлях для встановлення програми:")
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)

        self.browse_button = QPushButton("Обрати шлях...")
        self.browse_button.clicked.connect(self.select_folder)

        self.next_page = QPushButton("Далі")
        self.next_page.clicked.connect(self.show_progress_page)

        banner = QLabel()
        banner.setPixmap(QPixmap(get_resource_path("install.jpg")))
        banner.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(banner)
        layout.addWidget(self.path_to_install)
        layout.addWidget(self.path_edit)
        layout.addWidget(self.browse_button)
        layout.addWidget(self.next_page)
        page.setLayout(layout)

        return page

    def create_progress_page(self):
        page = QWidget()
        layout = QVBoxLayout()

        self.progress_label = QLabel("Очікується встановлення...")
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        self.cancel_button = QPushButton("Скасувати")
        self.cancel_button.clicked.connect(self.cancel_installation)

        banner = QLabel()
        banner.setPixmap(QPixmap(get_resource_path("install.jpg")))
        banner.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(banner)
        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.cancel_button)
        page.setLayout(layout)

        return page

    def finish_installation(self):
        page = QWidget()
        layout = QVBoxLayout()

        self.finish_label = QLabel("Програма встановлена успішно")

        self.complete_install = QPushButton("Завершити")
        self.complete_install.clicked.connect(QApplication.quit)

        banner = QLabel()
        banner.setPixmap(QPixmap(get_resource_path("install.jpg")))
        banner.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(banner)
        layout.addWidget(self.finish_label)
        layout.addWidget(self.complete_install)
        page.setLayout(layout)

        return page

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Оберіть папку для встановлення програми")
        if folder:
            self.path_edit.setText(folder)

    def show_progress_page(self):
        if not self.path_edit.text():
            QMessageBox.warning(self, "Помилка", "Ви не обрали папку для встановлення програми")
            return

        self.stacked_widget.setCurrentWidget(self.page_progress)
        self.start_installation()

    def start_installation(self):
        self.progress_label.setText("Відбувається встановлення...")
        self.progress_bar.setValue(0)

        self.installer_thread = InstallWorker(self.path_edit.text())
        self.installer_thread.progress_update.connect(self.progress_bar.setValue)
        self.installer_thread.progress_text.connect(self.progress_label.setText)
        self.installer_thread.finished.connect(self.installation_finished)
        self.installer_thread.start()

    def installation_finished(self):
        self.progress_label.setText("Встановлення завершено")

        all_info = get_information(os.path.splitdrive(self.path_edit.text())[0] + r'\\')
        print(all_info)
        keys_generation_data_signing(all_info)

        self.stacked_widget.setCurrentWidget(self.page_finish)

    def cancel_installation(self):
        if hasattr(self, "worker") and self.worker.isRunning():
            self.worker.stop()

        QMessageBox.information(self, "Скасовано", "Встановлення скасовано.")
        self.stacked_widget.setCurrentWidget(self.page_select_path)


class InstallWorker(QThread):
    progress_update = pyqtSignal(int)
    progress_text = pyqtSignal(str)

    def __init__(self, install_path):
        super().__init__()
        self.install_path = install_path
        self._is_running = True
        self.copied_files = []

    def run(self):
        files_to_copy = ["my_program.exe"]
        total_files = len(files_to_copy)

        os.makedirs(self.install_path, exist_ok=True)

        for i, file in enumerate(files_to_copy):
            if not self._is_running:
                self.cleanup()
                self.progress_text.emit("Встановлення скасовано")
                return

            t.sleep(1)
            src = get_resource_path(file)
            dest = os.path.join(self.install_path, file)

            try:
                shutil.copy(src, dest)
                self.copied_files.append(dest)
            except Exception as e:
                self.progress_text.emit(f"Помилка копіювання {file}: {e}")
                return

            self.progress_update.emit(int((i + 1) / total_files * 100))
            self.progress_text.emit(f"Копіювання {file}...")

        self.progress_text.emit("Програма встановлена")
        t.sleep(1)

    def stop(self):
        self._is_running = False

    def cleanup(self):
        for file in self.copied_files:
            try:
                if os.path.exists(file):
                    os.remove(file)
            except Exception as e:
                self.progress_text.emit(f"Не вдалося видалити {file}: {e}")


def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)


if __name__ == "__main__":
    app = QApplication([])
    window = Installer()
    window.show()
    app.exec()