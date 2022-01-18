import datetime
import os
import sqlite3
from sqlite3 import Error

class Database:
    def __init__(self, db_folder_path, db_file_name):
        self.db_folder_path = db_folder_path
        self.db_file_name = db_file_name

        if not os.path.isdir(db_folder_path):
            os.mkdir(db_folder_path)

        self.create_tables()

    def connect(self):
        conn = None
        try:
            conn = sqlite3.connect(os.path.join(self.db_folder_path, self.db_file_name))
        except Error as e:
            print(e)

        return conn

    def create_table(self, conn, query):
        try:
            c = conn.cursor()
            c.execute(query)
        except Error as e:
            print(e)

    def set_daily(self, member_id):
        sql = "UPDATE scores SET daily = ? WHERE id = ?"

        conn = self.connect()

        cursor = conn.cursor()
        cursor.execute(sql, (datetime.datetime.now(), member_id))
        conn.commit()

    def collected_daily(self, member_id):
        sql = "SELECT daily FROM scores WHERE id = ? AND CAST(daily AS DATE) = CAST( date('now') AS DATE)"

        conn = self.connect()

        cursor = conn.cursor()
        cursor.execute(sql, (member_id,))

        row = cursor.fetchone()

        if row is None:
            return False
        else:
            return True


    def create_message(self, member_id, message_id):
        sql = "INSERT INTO messages (id, message_id, message_datetime) VALUES (?, ?, ?)"

        conn = self.connect()

        cursor = conn.cursor()
        cursor.execute(sql, (member_id, message_id, datetime.datetime.now()))
        conn.commit()

    def get_messages_from_today(self, member_id):
        sql = "SELECT * FROM messages WHERE id = ? AND CAST(message_datetime AS DATE) = CAST( date('now') AS DATE)"

        conn = self.connect()

        cursor = conn.cursor()
        cursor.execute(sql, (member_id,))

        rows = cursor.fetchall()

        return rows

    def create_member(self, member_id):
        sql = "INSERT INTO scores (id, score) VALUES (?, ?)"

        conn = self.connect()

        cursor = conn.cursor()
        cursor.execute(sql, (member_id, 0))
        conn.commit()

    def set_score(self, member_id, score):
        sql = "UPDATE scores SET score = ? WHERE id = ?"

        conn = self.connect()

        cursor = conn.cursor()
        cursor.execute(sql, (score, member_id))
        conn.commit()

    def get_member(self, member_id):
        sql = "SELECT * FROM scores WHERE id = ?"

        conn = self.connect()

        cursor = conn.cursor()
        cursor.execute(sql, (member_id,))

        row = cursor.fetchone()

        return row

    def get_scores(self):
        sql = "SELECT * FROM scores ORDER BY score DESC"

        conn = self.connect()

        cursor = conn.cursor()
        cursor.execute(sql)

        rows = cursor.fetchall()

        return rows

    def create_tables(self):

        sql_create_admins_table = """ 
        CREATE TABLE IF NOT EXISTS admins (
            id varchar PRIMARY KEY
        ); """

        sql_create_scores_table = """ 
        CREATE TABLE IF NOT EXISTS scores (
            id varchar PRIMARY KEY,
            score int,
            daily timestamp             
        ); """

        sql_create_messages_table = """
        CREATE TABLE IF NOT EXISTS messages (
            id varchar,
            message_id varchar,
            message_datetime timestamp
        ); """

        # create a database connection
        conn = self.connect()

        # create tables
        if conn is not None:
            self.create_table(conn, sql_create_admins_table)
            self.create_table(conn, sql_create_scores_table)
            self.create_table(conn, sql_create_messages_table)

