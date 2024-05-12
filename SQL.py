import psycopg2
from psycopg2 import Error

def connect_to_postgres(Database, User, Password, Host, Port):
    connection = None
    cursor = None
    try:
        # Устанавливаем соединение с базой данных
        connection = psycopg2.connect(
            database=Database,
            user=User,
            password=Password,
            host=Host,
            port=Port
        )

        # Создаем курсор для выполнения SQL-запросов
        cursor = connection.cursor()

        # Выводим информацию о подключении
        print("Успешное подключение к базе данных PostgreSQL")

        # Возвращаем объекты подключения и курсора
        return connection, cursor

    except Error as e:
        print(f"Ошибка при подключении к базе данных PostgreSQL: {e}")
        # Закрываем соединение, если произошла ошибка
        if connection:
            connection.close()

    # Если возникла ошибка, возвращаем None для обоих объектов
    return None, None
def disconnect_from_postgres(connection):
    try:
        if connection:
            connection.close()
            print("Соединение с базой данных PostgreSQL закрыто")
        else:
            print("Нет активного соединения с базой данных")
    except Error as e:
        print(f"Ошибка при отключении от базы данных PostgreSQL: {e}")


def create_table(connection, table_name):
    try:
        if connection is None:
            print("Нет активного соединения с базой данных")
            return

        cursor = connection.cursor()

        columns = [
            "id SERIAL PRIMARY KEY",
            "name VARCHAR(255)",
            "age INT",
            "email VARCHAR(255)"
        ]

        # Формируем SQL-запрос для создания таблицы
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"

        # Выполняем SQL-запрос
        cursor.execute(query)
        connection.commit()

        print(f"Таблица {table_name} успешно создана")
    except Error as e:
        print(f"Ошибка при создании таблицы {table_name}: {e}")

def add_columns_to_table(connection, table_name, columns_to_add):
    try:
        if connection is None:
            print("Нет активного соединения с базой данных")
            return

        cursor = connection.cursor()

        # Формируем SQL-запрос для добавления столбцов к существующей таблице

        alter_query = f"ALTER TABLE {table_name} ADD COLUMN {columns_to_add}"

        # Выполняем SQL-запрос для добавления столбцов
        cursor.execute(alter_query)
        connection.commit()

        print(f"Столбцы добавлены успешно к таблице {table_name}")

    except Error as e:
        print(f"Ошибка при добавлении столбцов к таблице {table_name}: {e}")


def get_table_columns(connection, table_name):
    columns = []

    try:
        if connection is None:
            print("Нет активного соединения с базой данных")
            return columns

        cursor = connection.cursor()

        # Формируем SQL-запрос для получения информации о столбцах таблицы
        query = f"SELECT column_name, data_type, character_maximum_length, is_nullable " \
                f"FROM information_schema.columns " \
                f"WHERE table_name = '{table_name}'"

        # Выполняем SQL-запрос
        cursor.execute(query)

        # Получаем результаты запроса
        rows = cursor.fetchall()

        # Формируем описания столбцов в нужном формате
        for row in rows:
            column_name, data_type, max_length, is_nullable = row
            column_description = f"{column_name} {data_type}"
            if data_type in ['character', 'character varying'] and max_length is not None:
                column_description += f"({max_length})"
            if is_nullable == 'NO':
                column_description += " NOT NULL"

            columns.append(column_description)

    except Error as e:
        print(f"Ошибка при получении данных о столбцах таблицы {table_name}: {e}")
    print(columns)
    return columns
#Вывод таблицы
def fetch_table_data(connection, table_name):
    rows = []

    try:
        if connection is None:
            print("Нет активного соединения с базой данных")
            return rows

        cursor = connection.cursor()

        # Формируем SQL-запрос для выборки всех данных из указанной таблицы
        query = f"SELECT * FROM {table_name}"

        # Выполняем SQL-запрос
        cursor.execute(query)

        # Получаем результаты запроса
        rows = cursor.fetchall()

    except Error as e:
        print(f"Ошибка при выполнении SQL-запроса: {e}")

    return rows

def get_existing_identifiers(connection, table_name):
    existing_identifiers = set()

    try:
        # Извлекаем все данные из указанной таблицы
        table_data = fetch_table_data(connection, table_name)

        # Предположим, что идентификаторы находятся в первом столбце таблицы
        for row in table_data:
            if row:  # Проверяем, что строка не пустая
                existing_identifiers.add(row[0])  # Добавляем идентификатор в множество

    except Exception as e:
        print(f"Ошибка при получении существующих идентификаторов: {e}")

    return existing_identifiers

def insert_into_table(connection, table_name, data):
    try:
        if connection is None:
            print("Нет активного соединения с базой данных")
            return

        cursor = connection.cursor()

        # Формируем SQL-запрос для вставки данных в указанную таблицу
        # data должен быть в формате списка кортежей, где каждый кортеж представляет данные для одной строки
        placeholders = ', '.join(['%s'] * len(data[0])) if data else ''
        query = f"INSERT INTO {table_name} VALUES ({placeholders})"

        # Выполняем SQL-запрос
        cursor.executemany(query, data)
        connection.commit()

        print(f"Данные успешно добавлены в таблицу {table_name}")
    except Error as e:
        print(f"Ошибка при добавлении данных в таблицу {table_name}: {e}")



