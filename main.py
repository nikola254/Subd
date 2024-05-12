import sys
from PySide2.QtWidgets import QApplication, QMainWindow
from gui import Ui_MainWindow  # Импорт класса Ui_MainWindow из сгенерированного модуля


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Инициализация пользовательского интерфейса
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()