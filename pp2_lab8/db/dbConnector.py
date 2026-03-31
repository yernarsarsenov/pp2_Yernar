import psycopg2
from config.config import load_config
from db.PhoneBook import PhoneBook


class DBConnector:
    def __init__(self):
        self.config = load_config()

    def createTable(self):
        sql = '''
            CREATE SEQUENCE IF NOT EXISTS s;
            CREATE TABLE IF NOT EXISTS phone_nums (
                id         INTEGER DEFAULT nextval('s') PRIMARY KEY,
                first_name VARCHAR(255) NOT NULL,
                last_name  VARCHAR(255) NOT NULL,
                phone      VARCHAR(13)  NOT NULL
            );
        '''
        try:
            with psycopg2.connect(**self.config) as conn:
                with conn.cursor() as cur:
                    cur.execute(sql)
                conn.commit()
        except Exception as e:
            print("Error on creating table:", e)

    def getAllRecords(self):
        sql = "SELECT * FROM phone_nums ORDER BY id ASC"
        try:
            with psycopg2.connect(**self.config) as conn:
                with conn.cursor() as cur:
                    cur.execute(sql)
                    rows = cur.fetchall()
                    return [PhoneBook(*row) for row in rows]
        except Exception as e:
            print("Error on getAllRecords:", e)

    # --- ФУНКЦИЯ: поиск по паттерну ---
    def searchByPattern(self, pattern: str):
        sql = "SELECT * FROM search_contacts(%s)"
        try:
            with psycopg2.connect(**self.config) as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (pattern,))
                    rows = cur.fetchall()
                    return [PhoneBook(*row) for row in rows]
        except Exception as e:
            print("Error on searchByPattern:", e)

    # --- ПРОЦЕДУРА: upsert (insert or update) ---
    def upsertUser(self, user: PhoneBook):
        try:
            with psycopg2.connect(**self.config) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "CALL upsert_contact(%s, %s, %s)",
                        (user.first_name, user.last_name, user.phone)
                    )
                conn.commit()
        except Exception as e:
            print("Error on upsertUser:", e)

    # --- ПРОЦЕДУРА: bulk insert с валидацией ---
    def insertManyUsers(self, all_users: list[PhoneBook]):
        firsts = [u.first_name for u in all_users]
        lasts  = [u.last_name  for u in all_users]
        phones = [u.phone      for u in all_users]
        try:
            with psycopg2.connect(**self.config) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "CALL insert_many_contacts(%s, %s, %s)",
                        (firsts, lasts, phones)
                    )
                conn.commit()
                # читаем некорректные записи из вспомогательной таблицы
                with conn.cursor() as cur:
                    cur.execute("SELECT first_name, last_name, phone FROM invalid_contacts")
                    rows = cur.fetchall()
                    return [PhoneBook(0, r[0], r[1], r[2]) for r in rows]
        except Exception as e:
            print("Error on insertManyUsers:", e)
            return []

    # --- ФУНКЦИЯ: пагинация ---
    def getLimitOffset(self, limit: int, offset: int):
        sql = "SELECT * FROM get_contacts_paginated(%s, %s)"
        try:
            with psycopg2.connect(**self.config) as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (limit, offset))
                    rows = cur.fetchall()
                    return [PhoneBook(*row) for row in rows]
        except Exception as e:
            print("Error on getLimitOffset:", e)

    # --- ПРОЦЕДУРА: удаление по имени или телефону ---
    def deleteUser(self, value: str):
        try:
            with psycopg2.connect(**self.config) as conn:
                with conn.cursor() as cur:
                    cur.execute("CALL delete_contact(%s)", (value,))
                conn.commit()
        except Exception as e:
            print("Error on deleteUser:", e)