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
            "age INT",
            "name VARCHAR(255)"
        ]

        # Формируем SQL-запрос для создания таблицы
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"

        # Выполняем SQL-запрос
        cursor.execute(query)
        connection.commit()

        print(f"Таблица {table_name} успешно создана")
    except Error as e:
        print(f"Ошибка при создании таблицы {table_name}: {e}")

def add_columns_to_table(connection, table_name, columns_to_add, column):
    try:
        if connection is None:
            print("Нет активного соединения с базой данных")
            return

        cursor = connection.cursor()

        # Формируем SQL-запрос для добавления столбцов к существующей таблице
        print(columns_to_add)
        first1 = columns_to_add.split()[0].strip()
        print(first1)
        print(column)
        first2 = column.split()[0].strip()
        print(first2)
        alter_query = f"ALTER TABLE {table_name} ADD COLUMN {columns_to_add}"
        # Выполняем SQL-запрос для добавления столбцов
        cursor.execute(alter_query)
        connection.commit()

        # alter_query1 = f"ALTER TABLE {table_name} ALTER COLUMN {first1} SET AFTER {first2}"
        # cursor.execute(alter_query1)
        # connection.commit()
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
                f"WHERE table_name = '{table_name}'" \
                f"ORDER BY ordinal_position"

        # Выполняем SQL-запрос
        cursor.execute(query)

        # Получаем результаты запроса
        rows = cursor.fetchall()

        # Формируем описания столбцов в нужном формате
        for row in rows:
            column_name, data_type, max_length, is_nullable = row
            column_description = f"{column_name}"
            # if data_type in ['character', 'character varying'] and max_length is not None:
            #     column_description += f"({max_length})"
            # if is_nullable == 'NO':
            #     column_description += " NOT NULL"

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
        query = f"SELECT * FROM public.{table_name}"

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
    print(existing_identifiers)
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

def fetch_unit_data(connection):
    rows = []

    try:
        if connection is None:
            print("Нет активного соединения с базой данных")
            return rows

        cursor = connection.cursor()

        # SQL-запрос для выборки данных из таблицы units с объединением таблицы facultet
        query = """
            SELECT 
                f.name AS faculty_name,
                u.id_educ_building, -- Идентификатор учебного здания из таблицы 'unit'
                u.name AS unit_name,  -- Имя юнита из таблицы 'unit' с использованием алиаса 'unit_name'
                u.short_name AS faculty_short_name,  -- Краткое название факультета из таблицы 'unit' с использованием алиаса 'faculty_short_name'
                u.speciality                
            FROM 
                unit u
            LEFT JOIN
                facultet f ON u.id_fac = f.id_fac;
        """

        # Выполняем SQL-запрос
        cursor.execute(query)

        # Получаем результаты запроса
        rows = cursor.fetchall()

    except Error as e:
        print(f"Ошибка при выполнении SQL-запроса: {e}")

    return rows

def fetch_unit_data_educ_buiilding(connection):
    rows = []

    try:
        if connection is None:
            print("Нет активного соединения с базой данных")
            return rows

        cursor = connection.cursor()

        # SQL-запрос для выборки данных из таблицы units с объединением таблицы facultet
        query = """
            SELECT 
                f.name AS faculty_name,
                eb.name AS educ_building_name,  -- Имя учебного здания из таблицы 'educ_building'
                eb.address AS educ_building_address,  -- Адрес учебного здания из таблицы 'educ_building'
                u.name AS unit_name,  -- Имя юнита из таблицы 'unit' с использованием алиаса 'unit_name'
                u.short_name AS faculty_short_name,  -- Краткое название факультета из таблицы 'unit' с использованием алиаса 'faculty_short_name'
                u.speciality                
            FROM 
                unit u
            LEFT JOIN
                facultet f ON u.id_fac = f.id_fac
            LEFT JOIN
                educ_building eb ON u.id_educ_building = eb.id_educ_building;
        """

        # Выполняем SQL-запрос
        cursor.execute(query)

        # Получаем результаты запроса
        rows = cursor.fetchall()

    except Error as e:
        print(f"Ошибка при выполнении SQL-запроса: {e}")

    return rows

def fetch_unit_data_auditory(connection):
    rows = []

    try:
        if connection is None:
            print("Нет активного соединения с базой данных")
            return rows

        cursor = connection.cursor()

        # SQL-запрос для выборки данных из таблицы units с объединением таблицы facultet
        query = """
            SELECT 
                f.name AS faculty_name,
                eb.name AS educ_building_name,  -- Имя учебного здания из таблицы 'educ_building'
                eb.address AS educ_building_address,  -- Адрес учебного здания из таблицы 'educ_building'
                u.name AS unit_name,  -- Имя юнита из таблицы 'unit' с использованием алиаса 'unit_name'
                u.short_name AS faculty_short_name,  -- Краткое название факультета из таблицы 'unit' с использованием алиаса 'faculty_short_name'
                u.speciality,
                a.id_aud_type,
                a.name AS audit_name,
                a.capacity              
            FROM
                auditory a
            LEFT JOIN 
                unit u ON a.id_kaf = u.id_kaf
            LEFT JOIN
                facultet f ON u.id_fac = f.id_fac
            LEFT JOIN
                educ_building eb ON u.id_educ_building = eb.id_educ_building;
        """

        # Выполняем SQL-запрос
        cursor.execute(query)

        # Получаем результаты запроса
        rows = cursor.fetchall()

    except Error as e:
        print(f"Ошибка при выполнении SQL-запроса: {e}")

    return rows

def fetch_unit_data_auditory_types(connection):
    rows = []

    try:
        if connection is None:
            print("Нет активного соединения с базой данных")
            return rows

        cursor = connection.cursor()

        # SQL-запрос для выборки данных из таблицы units с объединением таблицы facultet
        query = """
            SELECT 
                f.name AS faculty_name,
                eb.name AS educ_building_name,  -- Имя учебного здания из таблицы 'educ_building'
                eb.address AS educ_building_address,  -- Адрес учебного здания из таблицы 'educ_building'
                u.name AS unit_name,  -- Имя юнита из таблицы 'unit' с использованием алиаса 'unit_name'
                u.short_name AS faculty_short_name,  -- Краткое название факультета из таблицы 'unit' с использованием алиаса 'faculty_short_name'
                a.name AS audit_name,
                at.name AS audit_type_name, 
                a.capacity,              
                u.speciality            
            FROM
                auditory a
            LEFT JOIN 
                unit u ON a.id_kaf = u.id_kaf
            LEFT JOIN
                facultet f ON u.id_fac = f.id_fac
            LEFT JOIN
                educ_building eb ON u.id_educ_building = eb.id_educ_building
            LEFT JOIN
                auditory_type at ON a.id_aud_type = at.id_aud_type;
        """

        # Выполняем SQL-запрос
        cursor.execute(query)   

        # Получаем результаты запроса
        rows = cursor.fetchall()

    except Error as e:
        print(f"Ошибка при выполнении SQL-запроса: {e}")

    return rows