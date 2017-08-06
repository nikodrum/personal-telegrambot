import sqlite3
import os
from datetime import datetime, timedelta, date


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
        database_path = "./data/{}".format(database)
        if os.path.exists(database_path):
            self.connection = sqlite3.connect(database_path)
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
                'INSERT INTO users VALUES (?,?,?)', (str(datetime.now()), u_id, False)
            ).fetchall()
            self.connection.commit()

    def post_file(self, file_id, file_type):
        """ Put user. """
        with self.connection:
            self.cursor.execute(
                'INSERT INTO files VALUES (?,?,?,?)', (str(datetime.now()), file_id, file_type, None)
            ).fetchall()
            self.connection.commit()

    def get_gif_id(self, date=None):
        """Get gif file id if exists."""
        with self.connection:
            if date:
                day = date.strptime(date, "%Y-%m-%d").date()
                next_day = date + timedelta(days=1)
                file_id = self.cursor.execute(
                    """SELECT file_id FROM files 
                       WHERE inserted_date = (
                          SELECT MAX(inserted_date) FROM files 
                          WHERE inserted_date > ? AND inserted_date < ? ) AND
                             type='gif'
                    """,
                    (str(day), str(next_day), )
                ).fetchall()[0]
            else:
                file_id = self.cursor.execute(
                    """SELECT file_id FROM files
                       WHERE inserted_date = ( 
                            SELECT MAX(inserted_date) FROM files) AND
                             type='gif'
                    """
                ).fetchall()[0]
            if file_id:
                return file_id
        return None

    def close(self):
        """ Close connection with DB """
        self.connection.close()
