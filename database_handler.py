import sqlite3
import os.path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get absolute path of current project
db_path = os.path.join(BASE_DIR, "birthdays.db")  # Gets the absolute path to our database file


def load_all_from_db():  # Load all bdays from database
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    query = 'SELECT * FROM bdays'
    r = cursor.execute(query).fetchall()
    return r


def save_to_db(name, date, gift='No', reminder=0):  # Add into db
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        cursor.execute("INSERT INTO bdays(name, date, gift, reminder) VALUES (?,?,?,?)", (name, date, gift, reminder))
        connection.commit()
    except Exception as e:
        print('Failed to save to db, received error: ', e)
        write_error_to_file(e)  # If any error is causes, append to textfile


def update_alert(_id, name, date, gift, reminder):
    try:
        con = sqlite3.connect(db_path)
        cursor = con.cursor()
        cursor.execute("UPDATE bdays SET name=?, date=?, gift=?, reminder=? WHERE ID=?", (name, date, gift, reminder, _id))
        con.commit()
    except Exception as e:
        print('Failed to update record, received error: ', e)
        write_error_to_file(e)


def delete_from_db(_id):
    try:
        print(';;', type(_id))
        con = sqlite3.connect(db_path)
        cursor = con.cursor()
        cursor.execute("DELETE FROM bdays WHERE ID=?", (_id,))  # _id needs to be in a tuple (), even if it's just one value
        con.commit()
        return f'Removed {str(cursor.rowcount)}.'  # Returns a formated string of the affected row from our database
    except Exception as e:
        print('Failed to delete record, received error: ', e)
        write_error_to_file(e)


def write_error_to_file(e):  # Append error message to a textfile
    try:
        f = open('error_logs.txt', 'a')  # Appends if exists, otherwise creates the file
        f.write(str(e))
        f.close()
    except Exception as e:
        print('Error when writing to file: ', e)
