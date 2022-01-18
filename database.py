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

    def create_member(self, member_id):
        sql = "INSERT INTO scores (id, score) VALUES (?, ?)"

        conn = self.connect()

        cursor = conn.cursor()
        cursor.execute(sql, (member_id, 0))
        conn.commit()

    def get_member(self, member_id):
        sql = "SELECT * FROM scores WHERE id = ?"

        conn = self.connect()

        cursor = conn.cursor()
        cursor.execute(sql, (member_id,))

        row = cursor.fetchone()

        return row

    def create_tables(self):

        sql_create_admins_table = """ 
        CREATE TABLE IF NOT EXISTS admins (
            id varchar PRIMARY KEY
        ); """

        sql_create_scores_table = """ 
        CREATE TABLE IF NOT EXISTS scores (
            id varchar PRIMARY KEY,
            score int             
        ); """

        # create a database connection
        conn = self.connect()

        # create tables
        if conn is not None:
            self.create_table(conn, sql_create_admins_table)
            self.create_table(conn, sql_create_scores_table)

