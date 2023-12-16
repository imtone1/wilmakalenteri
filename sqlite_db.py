#Tietokantana on SQLite3. Lisätietoa SQLite3:sta löytyy [täältä](https://docs.python.org/3/library/sqlite3.html).
import sqlite3
import json

from datetime import datetime, timedelta

def yhdista_tietokantaan():
    try:
        # Connect to DB and create a cursor
        sqliteConnection = sqlite3.connect("data/events.db")
        cursor = sqliteConnection.cursor()
        return cursor, sqliteConnection
 
    # Handle errors
    except sqlite3.Error as error:
        print('Error occurred - ', error)
 
def luo_tietokanta():
    sqliteConnection = sqlite3.connect("data/events.db")
    cursor = sqliteConnection.cursor()
    try:
        # # Connect to DB and create a cursor
        # sqliteConnection = sqlite3.connect(db_file)
        # cursor = sqliteConnection.cursor()
    
        # Write a query and execute it with cursor
        query = """ CREATE TABLE IF NOT EXISTS events (
                                        id integer PRIMARY KEY AUTOINCREMENT,
                                        summary text,
                                        description text UNIQUE,
                                        start text,
                                        stop text,
                                        created text DEFAULT CURRENT_TIMESTAMP
                                    ); """
        cursor.execute(query)
        # cursor.close()
    # Handle errors
    except sqlite3.Error as error:
        print('Error occurred - ', error)
    
    # # Close DB Connection irrespective of success
    # # or failure
    # finally:
    
    #     if sqliteConnection:
    #         sqliteConnection.close()
# test_luo_tietokanta(test_yhdista_tietokantaan()[0])  
def sulje_tietokanta(cursor):
    # Close the cursor
    cursor.close()

def lisaa_tietokantaan(event, cursor, connection):
    try:
        cursor.execute(f"""
        INSERT INTO events (summary, description, start, stop) VALUES
            ({event})""")
        connection.commit()
    except sqlite3.Error as error:
        print('Error occurred - ', error)

def lisaa_tietokantaantesti():
    try:
        connection = sqlite3.connect("data/events.db")
        cursor = connection.cursor()
        event = f"'testititle', 'notesdescription', '2023-08-21T00:00:00', '2023-08-21T01:00:00'"
        cursor.execute(f"""
        INSERT INTO events (summary, description, start, stop) VALUES
            ({event})""")
        connection.commit()
        cursor.close()
    except sqlite3.Error as error:
        print('Error occurred - ', error)
    


#testataan mitä tallennettu
def hae_tietokantasta():
    sqliteConnection = sqlite3.connect("data/events.db")
    cursor = sqliteConnection.cursor()
    #Valitaan kaikki
    cursor.execute("SELECT * FROM events")
    rows = cursor.fetchall()
    data = []
    # Print all rows
    for row in rows:
        data.append({"summary": row[1], "description": row[2], "start": row[3], "stop": row[4], "created": row[5]})
    tallenna_data_tiedostoon(data, "data/new_data.txt")
    # Close the cursor
    cursor.close()
    if sqliteConnection:
          sqliteConnection.close()


#tallennetaan data tiedostoon
def tallenna_data_tiedostoon(data, file_name):
    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def main():
    luo_tietokanta()
    lisaa_tietokantaantesti()

if __name__ == "__main__":
  main()