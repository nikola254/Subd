from PySide2.QtCore import (QCoreApplication, QDate, QDateTime, QMetaObject,
                            QObject, QPoint, QRect, QSize, QTime, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
                           QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter,
                           QPixmap, QRadialGradient, QStandardItemModel, QStandardItem)
from PySide2.QtWidgets import *
from SQL import (connect_to_postgres, disconnect_from_postgres,
                 create_table, add_columns_to_table, get_table_columns,
                 fetch_table_data, insert_into_table, get_existing_identifiers,
                 fetch_unit_data, fetch_unit_data_educ_buiilding, fetch_unit_data_auditory,
                 fetch_unit_data_auditory_types)

#Создание нового окна для добавления данных в таблицу
class TableDataEntry(QDialog):
    def __init__(self, columns, existing_identifiers, table_name, connection1):
        super().__init__()

        self.columns = columns
        self.existing_identifiers = existing_identifiers
        self.table_name = table_name
        self.connection1 = connection1
        self.collected_data = []

        self.table = QTableWidget()
        self.btn_add_row = QPushButton('Add Row')
        self.btn_add_row.clicked.connect(self.add_empty_row)
        self.resize(600, 400)

        self.btn_save = QPushButton('Save')
        self.btn_save.clicked.connect(self.save_data)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addWidget(self.btn_add_row)
        layout.addWidget(self.btn_save)

        self.setLayout(layout)

        self.setup_table()

    def setup_table(self):
        self.table.setColumnCount(len(self.columns))
        self.table.setHorizontalHeaderLabels(self.columns)

    def add_empty_row(self):
        row_count = self.table.rowCount()
        self.table.insertRow(row_count)

        for col in range(len(self.columns)):
            item = QLineEdit()
            self.table.setCellWidget(row_count, col, item)

    def save_data(self):
        self.collected_data = []

        for row in range(self.table.rowCount()):
            row_data = []
            for col in range(self.table.columnCount()):
                widget = self.table.cellWidget(row, col)
                if isinstance(widget, QLineEdit):
                    row_data.append(widget.text())
            if row_data:
                self.collected_data.append(tuple(row_data))

        existing_identifiers = get_existing_identifiers(self.connection1, self.table_name)
        identifiers_set = set(existing_identifiers)
        duplicate_identifiers = set()

        for row_data in self.collected_data:
            identifier = row_data[0] if row_data else None
            if identifier in identifiers_set:
                duplicate_identifiers.add(identifier)
            else:
                identifiers_set.add(identifier)

        if duplicate_identifiers:
            QMessageBox.warning(self, "Ошибка",
                                f"Идентификатор(ы) {', '.join(duplicate_identifiers)} уже существует(ют). Пожалуйста, исправьте и попробуйте снова.",
                                QMessageBox.Ok)
        else:
            self.accept()  # Закрываем диалог, передавая QDialog.Accepted

#Создания нового окна для того чтобы создавать столбцы
class AddColumnDialog(QDialog):
    def __init__(self):
        super().__init__()

        # Определение основных элементов интерфейса диалога
        self.setWindowTitle("Добавление столбца")
        self.layout = QVBoxLayout()

        # Выпадающий список для выбора типа столбца
        self.type_label = QLabel("Тип столбца:")
        self.type_combobox = QComboBox()
        self.type_combobox.addItems(["INTEGER", "VARCHAR", "BOOLEAN", "DATE"])  # Примеры типов данных
        self.layout.addWidget(self.type_label)
        self.layout.addWidget(self.type_combobox)

        # Поле для ввода имени столбца
        self.name_label = QLabel("Имя столбца:")
        self.name_lineedit = QLineEdit()
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.name_lineedit)

        # Опция для выбора PRIMARY KEY
        self.primary_key_checkbox = QCheckBox("PRIMARY KEY")
        self.layout.addWidget(self.primary_key_checkbox)

        # Поле для ввода длины столбца
        self.length_label = QLabel("Длина столбца (необязательно):")
        self.length_lineedit = QLineEdit()
        self.layout.addWidget(self.length_label)
        self.layout.addWidget(self.length_lineedit)

        # Кнопка подтверждения добавления столбца
        self.add_button = QPushButton("Добавить столбец")
        self.add_button.clicked.connect(self.on_add_column)
        self.layout.addWidget(self.add_button)

        self.setLayout(self.layout)

    def on_add_column(self):
        column_type = self.type_combobox.currentText()
        column_name = self.name_lineedit.text().strip()
        is_primary_key = self.primary_key_checkbox.isChecked()
        column_length = self.length_lineedit.text().strip()

        if not column_name:
            QMessageBox.critical(self, "Ошибка", "Введите имя столбца", QMessageBox.Ok)
            return

        column_definition = f"{column_name} {column_type}"
        if column_length:
            column_definition += f"({column_length})"

        if is_primary_key:
            column_definition += " PRIMARY KEY"

        self.accept()
        self.column_definition = column_definition

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        self.connection1 = None

        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setGeometry(QRect(0, 0, 801, 601))
        self.welcome = QWidget()
        self.welcome.setObjectName(u"welcome")
        self.Next = QPushButton(self.welcome)
        self.Next.setObjectName(u"Next")
        self.Next.setGeometry(QRect(60, 480, 681, 61))
        self.Next.clicked.connect(self.showNextPage)
        self.label = QLabel(self.welcome)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(100, 220, 601, 181))
        font = QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setWordWrap(True)
        self.label_2 = QLabel(self.welcome)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(90, 100, 641, 101))
        font1 = QFont()
        font1.setPointSize(19)
        font1.setBold(True)
        font1.setWeight(75)
        self.label_2.setFont(font1)
        self.stackedWidget.addWidget(self.welcome)

        self.connection = QWidget()
        self.connection.setObjectName(u"connection")
        self.verticalLayoutWidget_3 = QWidget(self.connection)
        self.verticalLayoutWidget_3.setObjectName(u"verticalLayoutWidget_3")
        self.verticalLayoutWidget_3.setGeometry(QRect(60, 50, 671, 361))
        self.verticalLayout_6 = QVBoxLayout(self.verticalLayoutWidget_3)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.label_3 = QLabel(self.verticalLayoutWidget_3)
        self.label_3.setObjectName(u"label_3")
        font2 = QFont()
        font2.setPointSize(11)
        self.label_3.setFont(font2)
        self.label_3.setAlignment(Qt.AlignCenter)

        self.verticalLayout_6.addWidget(self.label_3)

        self.lineEdit_2 = QLineEdit(self.verticalLayoutWidget_3)
        self.lineEdit_2.setObjectName(u"lineEdit_2")
        self.lineEdit_2.setFrame(False)
        self.lineEdit_2.setAlignment(Qt.AlignCenter)

        self.verticalLayout_6.addWidget(self.lineEdit_2)

        self.label_4 = QLabel(self.verticalLayoutWidget_3)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setFont(font2)
        self.label_4.setAlignment(Qt.AlignCenter)

        self.verticalLayout_6.addWidget(self.label_4)

        self.lineEdit_3 = QLineEdit(self.verticalLayoutWidget_3)
        self.lineEdit_3.setObjectName(u"lineEdit_3")
        self.lineEdit_3.setFrame(False)
        self.lineEdit_3.setAlignment(Qt.AlignCenter)

        self.verticalLayout_6.addWidget(self.lineEdit_3)

        self.label_5 = QLabel(self.verticalLayoutWidget_3)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setFont(font2)
        self.label_5.setAlignment(Qt.AlignCenter)

        self.verticalLayout_6.addWidget(self.label_5)

        self.lineEdit_4 = QLineEdit(self.verticalLayoutWidget_3)
        self.lineEdit_4.setObjectName(u"lineEdit_4")
        self.lineEdit_4.setFrame(False)
        self.lineEdit_4.setAlignment(Qt.AlignCenter)

        self.verticalLayout_6.addWidget(self.lineEdit_4)

        self.label_6 = QLabel(self.verticalLayoutWidget_3)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setFont(font2)
        self.label_6.setAlignment(Qt.AlignCenter)

        self.verticalLayout_6.addWidget(self.label_6)

        self.lineEdit_5 = QLineEdit(self.verticalLayoutWidget_3)
        self.lineEdit_5.setObjectName(u"lineEdit_5")
        self.lineEdit_5.setFrame(False)
        self.lineEdit_5.setAlignment(Qt.AlignCenter)

        self.verticalLayout_6.addWidget(self.lineEdit_5)

        self.label_7 = QLabel(self.verticalLayoutWidget_3)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setFont(font2)
        self.label_7.setAlignment(Qt.AlignCenter)

        self.verticalLayout_6.addWidget(self.label_7)

        self.lineEdit_6 = QLineEdit(self.verticalLayoutWidget_3)
        self.lineEdit_6.setObjectName(u"lineEdit_6")
        self.lineEdit_6.setFrame(False)
        self.lineEdit_6.setAlignment(Qt.AlignCenter)

        self.verticalLayout_6.addWidget(self.lineEdit_6)

        self.default_2 = QPushButton(self.connection)
        self.default_2.setObjectName(u"default_2")
        self.default_2.setGeometry(QRect(600, 420, 131, 31))
        self.default_2.clicked.connect(lambda: self.set_default_values(self.line_edit_widgets))
        self.connect = QPushButton(self.connection)
        self.connect.setObjectName(u"connect")
        self.line_edit_widgets = [self.lineEdit_2, self.lineEdit_3, self.lineEdit_4, self.lineEdit_5, self.lineEdit_6]
        self.connect.clicked.connect(lambda: self.on_connect_clicked(self.line_edit_widgets))
        self.connect.setGeometry(QRect(250, 460, 481, 71))
        font3 = QFont()
        font3.setPointSize(15)
        self.connect.setFont(font3)
        self.info = QPushButton(self.connection)
        self.info.setObjectName(u"info")
        self.info.setGeometry(QRect(640, 10, 93, 28))
        self.disconnect = QPushButton(self.connection)
        self.disconnect.setObjectName(u"disconnect")
        self.disconnect.setGeometry(QRect(60, 460, 181, 71))
        self.disconnect.setFont(font3)
        self.disconnect.clicked.connect(lambda: self.on_disconnect_clicked())
        self.stackedWidget.addWidget(self.connection)

        self.main = QWidget()
        self.main.setObjectName(u"main")
        self.horizontalLayoutWidget = QWidget(self.main)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(20, 370, 751, 211))
        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")

        self.createTable = QPushButton(self.horizontalLayoutWidget)
        self.createTable.setObjectName(u"createTable")
        self.createTable.setFont(font2)
        self.createTable.clicked.connect(lambda: self.on_create_table_clicked())

        self.verticalLayout_4.addWidget(self.createTable)

        self.addColumn = QPushButton(self.horizontalLayoutWidget)
        self.addColumn.setObjectName(u"addColumn")
        self.addColumn.setFont(font2)
        self.addColumn.clicked.connect(self.on_add_column_on_table_clicked)

        self.verticalLayout_4.addWidget(self.addColumn)

        self.output_table = QPushButton(self.horizontalLayoutWidget)
        self.output_table.setObjectName(u"addColumn")
        self.output_table.setFont(font2)
        self.output_table.clicked.connect(self.output_table_on_clicked)

        self.verticalLayout_4.addWidget(self.output_table)

        self.addData = QPushButton(self.horizontalLayoutWidget)
        self.addData.setObjectName(u"addData")
        self.addData.setFont(font2)
        self.addData.clicked.connect(self.addData_on_table_on_clicked)

        self.verticalLayout_4.addWidget(self.addData)

        self.execute = QPushButton(self.horizontalLayoutWidget)
        self.execute.setObjectName(u"execute")
        self.execute.setFont(font2)
        self.execute.clicked.connect(self.connect_next_table_audit_types)

        self.verticalLayout_4.addWidget(self.execute)

        self.horizontalLayout.addLayout(self.verticalLayout_4)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.deleteTable = QPushButton(self.horizontalLayoutWidget)
        self.deleteTable.setObjectName(u"deleteTable")
        self.deleteTable.setFont(font2)
        self.deleteTable.clicked.connect(self.connect_table)

        self.verticalLayout_5.addWidget(self.deleteTable)

        self.deleteColumn = QPushButton(self.horizontalLayoutWidget)
        self.deleteColumn.setObjectName(u"deleteColumn")
        self.deleteColumn.setFont(font2)
        self.deleteColumn.clicked.connect(self.connect_next_table)

        self.verticalLayout_5.addWidget(self.deleteColumn)

        self.deleteData = QPushButton(self.horizontalLayoutWidget)
        self.deleteData.setObjectName(u"deleteData")
        self.deleteData.setFont(font2)
        self.deleteData.clicked.connect(self.connect_next_table_audit)

        self.verticalLayout_5.addWidget(self.deleteData)

        self.cleaner = QPushButton(self.horizontalLayoutWidget)
        self.cleaner.setObjectName(u"cleaner")
        self.cleaner.setFont(font2)
        self.verticalLayout_5.addWidget(self.cleaner)
        self.cleaner.clicked.connect(self.clean_output_clicked)

        self.Return = QPushButton(self.horizontalLayoutWidget)
        self.Return.setObjectName(u"Return")
        self.Return.setFont(font2)
        self.Return.clicked.connect(self.return_to_previous_page)

        self.verticalLayout_5.addWidget(self.Return)

        self.horizontalLayout.addLayout(self.verticalLayout_5)

        self.output = QTableWidget(self.main)
        self.output.setObjectName(u"output")
        self.output.setGeometry(QRect(20, 10, 761, 271))
        # Создаем модель данных для QListView
        self.model = QStandardItemModel(self.output)

        self.input = QLineEdit(self.main)
        self.input.setObjectName(u"input")
        self.input.setGeometry(QRect(30, 320, 731, 41))

        self.label_8 = QLabel(self.main)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setGeometry(QRect(20, 290, 761, 20))
        font4 = QFont()
        font4.setPointSize(10)
        self.label_8.setFont(font4)
        self.label_8.setAlignment(Qt.AlignCenter)
        self.stackedWidget.addWidget(self.main)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(MainWindow)
        # Функция которая реализует отключение от подключенной базы данных

    def on_disconnect_clicked(self):
        if self.connection1 is not None:
            disconnect_from_postgres(self.connection1)  # Закрываем соединение
            QMessageBox.information(None, "Успешное отключение", "Отключение от базы данных произведено успешно",
                                    QMessageBox.Ok)
            self.connection1 = None  # Сбрасываем ссылку на соединение
        else:
            QMessageBox.critical(None, "Ошибка", "Нет активного соединения с базой данных", QMessageBox.Ok)

    # Функция которая собирает данные из полей для ввода
    def get_connection_data(self, line_edit_widgets):
        data = []
        for i in range(2, 7):  # Start from index 2 (lineEdit_2) up to index 6 (lineEdit_6)
            line_edit_name = f"lineEdit_{i}"
            for line_edit in line_edit_widgets:
                if line_edit.objectName() == line_edit_name and isinstance(line_edit, QLineEdit):
                    data.append(line_edit.text().strip())
                    break
        return data

    # Функция реализует подключение при нажатии
    def on_connect_clicked(self, line_edit_widgets):
        connection_data = self.get_connection_data(line_edit_widgets)
        if all(connection_data) and len(connection_data) == 5:
            Database, User, Password, Host, Port = connection_data
            # Proceed with database connection using Database, User, Password, Host, Port
            self.connection1, cursor = connect_to_postgres(Database, User, Password, Host, Port)

            successful_message = f"Успешное подключение к базе данных {Database}"
            QMessageBox.information(None, "Успешное подключение", successful_message, QMessageBox.Ok)
            self.showNextPage()
        else:
            error_message = "Please fill all required fields."
            QMessageBox.critical(None, "Error", error_message, QMessageBox.Ok)

    # Функция для логики кнопки default
    def set_default_values(self, line_edit_widgets):
        values = ["SUBD_1", "postgres", "root", "localhost", "5432"]
        for line_edit, value in zip(line_edit_widgets, values):
            line_edit.setText(value)

    def socr(self, columns):
        self.output.setColumnCount(len(columns))

        # Устанавливаем заголовки столбцов на основе структуры
        self.output.setHorizontalHeaderLabels(columns)

        # Отключаем редактирование ячеек (только для отображения)
        self.output.setEditTriggers(QTableWidget.NoEditTriggers)

        # Устанавливаем размеры столбцов по содержимому
        self.output.resizeColumnsToContents()
        # Выводим таблицу
        self.output.show()

    def on_create_table_clicked(self):
        table_name = self.input.text().strip()
        # Проверим, что есть активное соединение с базой данных
        if self.connection1 is not None:
            # Создадим таблицу
            create_table(self.connection1, table_name)

            # Выведем информационное сообщение об успешном создании таблицы
            QMessageBox.information(self.centralwidget, "Успешное создание таблицы",
                                    f"Таблица {table_name} успешно создана", QMessageBox.Ok)
            # Очищаем содержимое QLineEdit

            self.model.clear()
            columns = [
            "id SERIAL PRIMARY KEY",
            "age INT",
            "name VARCHAR(255)"
        ]
            self.socr(columns)
        else:
            # Выведем сообщение об ошибке отсутствия активного соединения
            QMessageBox.critical(self.centralwidget, "Ошибка", "Нет активного соединения с базой данных",
                                 QMessageBox.Ok)

    #Функуия для добавления колонок в таблицу
    def on_add_column_on_table_clicked(self):
        table_name = self.input.text().strip()
        dialog = AddColumnDialog()
        columns = get_table_columns(self.connection1, table_name)
        last_column = columns[-1]
        print(columns)
        if dialog.exec_() == QDialog.Accepted:
            column_definition = dialog.column_definition
            print(column_definition)
            if column_definition:
                add_columns_to_table(self.connection1, table_name, column_definition, last_column)
                print(f"Добавление столбца: {column_definition}")
        self.socr(columns)

    #Функция для вывода таблицы
    def output_table_on_clicked(self):
        table_name = self.input.text().strip()
        columns = get_table_columns(self.connection1, table_name)
        rows = fetch_table_data(self.connection1, table_name)
        self.clean_output_clicked()
        # Устанавливаем количество столбцов и заголовки столбцов
        self.output.setColumnCount(len(columns))
        self.output.setHorizontalHeaderLabels(columns)

        # Загружаем данные таблицы в QTableWidget
        self.output.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, cell_value in enumerate(row_data):
                item = QTableWidgetItem(str(cell_value))
                self.output.setItem(row_idx, col_idx, item)

        # Устанавливаем размеры столбцов по содержимому
        self.output.resizeColumnsToContents()

    #Функция для ввода данных в талицу
    def addData_on_table_on_clicked(self):
        table_name = self.input.text().strip()
        columns = get_table_columns(self.connection1, table_name)
        existing_identifiers = get_existing_identifiers(self.connection1, table_name)

        # Создаем диалоговое окно TableDataEntry с текущим окном в качестве родителя
        dialog = TableDataEntry(columns, existing_identifiers, table_name, self.connection1)

        result = dialog.exec_()

        # После завершения диалога, можно проверить результат
        if result == QDialog.Accepted:
            # Здесь можно получить данные из диалога
            data = dialog.collected_data
            if data:
                try:
                    insert_into_table(self.connection1,table_name ,data)
                    print("Данные успешно добавлены в таблицу.")
                except:
                    print("fdlkdf")
            else:
                print("Данные не были введены или не прошли проверку уникальности.")
        else:
            print("Действие отменено или закрыто окно")

#Функция которая соединяет две таблицы unit и facultets
    def connect_table(self):
        table_name = self.input.text().strip()
        rows = fetch_unit_data(self.connection1)
        columns = [
            "Название факультета",
            "Здание",
            "Название кафедры",
            "Короткое название",
            "Спец",
        ]
        self.clean_output_clicked()
        # Устанавливаем количество столбцов и заголовки столбцов
        self.output.setColumnCount(len(columns))
        self.output.setHorizontalHeaderLabels(columns)

        # Загружаем данные таблицы в QTableWidget
        self.output.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, cell_value in enumerate(row_data):
                item = QTableWidgetItem(str(cell_value))
                self.output.setItem(row_idx, col_idx, item)

        # Устанавливаем размеры столбцов по содержимому
        self.output.resizeColumnsToContents()

#Функция которая соединяет unit, facultets, educ_buildings
    def connect_next_table(self):
        table_name = self.input.text().strip()
        rows = fetch_unit_data_educ_buiilding(self.connection1)
        columns = [
            "Название факультета",
            "Имя учебного здания",
            "Сокращенно",
            "Название кафедры",
            "Короткое название",
            "Спец",
        ]
        self.clean_output_clicked()
        # Устанавливаем количество столбцов и заголовки столбцов
        self.output.setColumnCount(len(columns))
        self.output.setHorizontalHeaderLabels(columns)

        # Загружаем данные таблицы в QTableWidget
        self.output.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, cell_value in enumerate(row_data):
                item = QTableWidgetItem(str(cell_value))
                self.output.setItem(row_idx, col_idx, item)

        # Устанавливаем размеры столбцов по содержимому
        self.output.resizeColumnsToContents()

    def connect_next_table_audit(self):
        table_name = self.input.text().strip()
        rows = fetch_unit_data_auditory(self.connection1)
        columns = [
            "Название факультета",
            "Имя учебного здания",
            "Сокращенно",
            "Название кафедры",
            "Короткое название",
            "Спец",
            "Тип ауидт",
            "Номер аудит",
            "Посдка",
        ]
        self.clean_output_clicked()
        # Устанавливаем количество столбцов и заголовки столбцов
        self.output.setColumnCount(len(columns))
        self.output.setHorizontalHeaderLabels(columns)

        # Загружаем данные таблицы в QTableWidget
        self.output.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, cell_value in enumerate(row_data):
                item = QTableWidgetItem(str(cell_value))
                self.output.setItem(row_idx, col_idx, item)

        # Устанавливаем размеры столбцов по содержимому
        self.output.resizeColumnsToContents()

    def connect_next_table_audit_types(self):
        table_name = self.input.text().strip()
        rows = fetch_unit_data_auditory_types(self.connection1)
        columns = [
            "Название факультета",
            "Имя учебного здания",
            "Сокращенно",
            "Название кафедры",
            "Короткое название",
            "Номер аудит",
            "Тип ауидт",
            "Посaдка",
            "Спец",
        ]
        self.clean_output_clicked()
        # Устанавливаем количество столбцов и заголовки столбцов
        self.output.setColumnCount(len(columns))
        self.output.setHorizontalHeaderLabels(columns)

        # Загружаем данные таблицы в QTableWidget
        self.output.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, cell_value in enumerate(row_data):
                item = QTableWidgetItem(str(cell_value))
                self.output.setItem(row_idx, col_idx, item)

        # Устанавливаем размеры столбцов по содержимому
        self.output.resizeColumnsToContents()
        #Функция которя очищает окно вывода
    def clean_output_clicked(self):
        self.clear_table_widget(self.output)
    #Побочная функция для очистки поля
    def clear_table_widget(self, table_widget):
        table_widget.clearContents()  # Очищаем содержимое ячеек таблицы

        while table_widget.rowCount() > 0:
            table_widget.removeRow(0)  # Удаляем все строки из таблицы

        while table_widget.columnCount() > 0:
            table_widget.removeColumn(0)
# Функции для переключения между страницами
    def showNextPage(self):
        # Получаем текущий индекс страницы
        currentIndex = self.stackedWidget.currentIndex()

        # Переходим на следующую страницу (увеличиваем индекс на 1)
        nextIndex = currentIndex + 1
        if nextIndex < self.stackedWidget.count():
            self.stackedWidget.setCurrentIndex(nextIndex)
#Функция для возвращения на предыдущую старницу
    def return_to_previous_page(self):
        # Получаем текущий индекс страницы
        current_index = self.stackedWidget.currentIndex()
        # Проверяем, что текущий индекс не является первым (главной страницей)
        if current_index > 0:
            # Уменьшаем индекс на 1, чтобы вернуться на предыдущую страницу
            new_index = current_index - 1
            self.stackedWidget.setCurrentIndex(new_index)
            self.model.clear()
        else:
            # Если текущая страница - первая (главная), можно выполнить другое действие
            print("Already on the first page")


    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.Next.setText(
            QCoreApplication.translate("MainWindow", u"\u041f\u0440\u043e\u0434\u043e\u043b\u0436\u0438\u0442\u044c",
                                       None))
        self.label.setText(QCoreApplication.translate("MainWindow",
                                                      u"\u0414\u0430\u043d\u043d\u0430\u044f \u043f\u0440\u043e\u0433\u0440\u0430\u043c\u043c\u0430 \u043f\u0440\u0435\u0434\u043d\u0430\u0437\u043d\u0430\u0447\u0435\u043d\u0430 \u0434\u043b\u044f \u0434\u043b\u044f \u0444\u043e\u0440\u043c\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u044f \u0443 \u043e\u0431\u044b\u0447\u043d\u044b\u0445 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u0439 \u043f\u0435\u0440\u0432\u0438\u0447\u043d\u044b\u0445 \u0437\u043d\u0430\u043d\u0438\u0439 \u0441 \u0431\u0430\u0437\u0430\u043c\u0438 \u0434\u0430\u043d\u043d\u044b\u0445 \u0438 \u0441\u043f\u043e\u0441\u043e\u0431\u0430\u043c\u0438 \u0432\u0437\u0430\u0438\u043c\u043e\u0434\u0435\u0439\u0441\u0442\u0432\u0438\u044f \u0441 \u043d\u0438\u043c\u0438",
                                                      None))
        self.label_2.setText(QCoreApplication.translate("MainWindow",
                                                        u"\u0414\u043e\u0431\u0440\u043e \u043f\u043e\u0436\u0430\u043b\u043e\u0432\u0430\u0442\u044c \u0432 SQL Workbench",
                                                        None))
        self.label_3.setText(QCoreApplication.translate("MainWindow",
                                                        u"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u0438\u043c\u044f \u0431\u0430\u0437\u044b \u0434\u0430\u043d\u043d\u044b\u0445",
                                                        None))
        self.label_4.setText(QCoreApplication.translate("MainWindow",
                                                        u"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u0438\u043c\u044f \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f",
                                                        None))
        self.label_5.setText(QCoreApplication.translate("MainWindow",
                                                        u"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043f\u0430\u0440\u043e\u043b\u044c",
                                                        None))
        self.label_6.setText(
            QCoreApplication.translate("MainWindow", u"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 Host", None))
        self.label_7.setText(
            QCoreApplication.translate("MainWindow", u"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 Port", None))
        self.default_2.setText(QCoreApplication.translate("MainWindow",
                                                          u"\u041f\u043e \u0443\u043c\u043e\u043b\u0447\u0430\u043d\u0438\u044e",
                                                          None))
        self.connect.setText(QCoreApplication.translate("MainWindow",
                                                        u"\u041f\u043e\u0434\u043a\u043b\u044e\u0447\u0438\u0442\u044c\u0441\u044f",
                                                        None))
        self.info.setText(
            QCoreApplication.translate("MainWindow", u"\u0418\u043d\u0441\u0442\u0440\u0443\u043a\u0446\u0438\u044f",
                                       None))
        self.disconnect.setText(QCoreApplication.translate("MainWindow",
                                                           u"\u041e\u0442\u043a\u043b\u044e\u0447\u0438\u0442\u044c\u0441\u044f",
                                                           None))
        self.createTable.setText(QCoreApplication.translate("MainWindow",
                                                            u"\u0421\u043e\u0437\u0434\u0430\u0442\u044c \u0442\u0430\u0431\u043b\u0438\u0446\u0443",
                                                            None))
        self.addColumn.setText(QCoreApplication.translate("MainWindow",
                                                          u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u0441\u0442\u043e\u043b\u0431\u0435\u0446",
                                                          None))
        self.addData.setText(QCoreApplication.translate("MainWindow",
                                                        u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u0434\u0430\u043d\u043d\u044b\u0435",
                                                        None))
        self.execute.setText(QCoreApplication.translate("MainWindow",
                                                        u"Соединение всех таблиц",
                                                        None))
        self.deleteTable.setText(QCoreApplication.translate("MainWindow",
                                                            u"Вывод в простом виде",
                                                            None))
        self.deleteColumn.setText(QCoreApplication.translate("MainWindow",
                                                             u"Прямое соедение 2 таблиц",
                                                             None))
        self.deleteData.setText(QCoreApplication.translate("MainWindow", u"Прямое соединение 3 таблиц", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow",
                                                        u"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043b\u0438\u0431\u043e \u0438\u043c\u044f \u0442\u0430\u0431\u043b\u0438\u0446\u044b, \u0438\u043c\u044f \u0441\u0442\u043e\u043b\u0431\u0446\u0430, \u0435\u0433\u043e \u0444\u043e\u0440\u043c\u0430\u0442, \u0434\u0430\u043d\u043d\u044b\u0435 \u0434\u043b\u044f \u0434\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u0438\u044f, SQL \u0437\u0430\u043f\u0440\u043e\u0441",
                                                        None))
        self.Return.setText(QCoreApplication.translate("MainWindow", u"Назад", None))
        self.output_table.setText(QCoreApplication.translate("MainWindow", u"Вывести таблицу", None))
        self.cleaner.setText(QCoreApplication.translate("MainWindow", u"Очистить поле", None))
    # retranslateUi
