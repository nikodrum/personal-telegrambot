import sqlite3
import os
import time
from datetime import datetime


def init_database(name):
    connection = sqlite3.connect("./data/{}.db".format(name))
    c = connection.cursor()

    c.execute(
        '''CREATE TABLE users (
                inserted_date text,
                user_id int,
                daily_gif bool
        )''')
    c.execute(
        '''CREATE TABLE files (
                inserted_date text,
                file_id text,
                type text,
                properties text
        )''')
    connection.commit()
    connection.close()


class SQLighter:

    def __init__(self, database):
        if os.path.exists("./data/base/{}.db".format(database)):
            self.connection = sqlite3.connect(database)
        else:
            init_database(name="bot")
        self.cursor = self.connection.cursor()

    def select_all_users(self):
        """ Getting all users """
        with self.connection:
            return self.cursor.execute('SELECT * FROM users').fetchall()

    def check_user(self, u_id):
        """ Check user by user_id """
        with self.connection:
            return 1 == len(self.cursor.execute(
                'SELECT * FROM users WHERE user_id = ?', (u_id,)
            ).fetchall())

    def post_user(self, u_id):
        """ Put user. """
        with self.connection:
            self.cursor.execute(
                'INSERT INTO users VALUES (?,?)', (str(datetime.now()), u_id, False)
            ).fetchall()
            self.connection.commit()

    def post_file(self, file_id, file_type):
        """ Put user. """
        with self.connection:
            self.cursor.execute(
                'INSERT INTO files VALUES (?,?,?,?)', (str(datetime.now()), file_id, file_type, None)
            ).fetchall()
            self.connection.commit()

    def close(self):
        """ Close connection with DB """
        self.connection.close()
