#Playwright
from playwright.sync_api import Page
import sqlite3
import json
# config.py
from config import login_url, login, password, wilma_person
from datetime import datetime, timedelta

def test_yhdista_tietokantaan():
    try:
        # Connect to DB and create a cursor
        # Connect to DB and create a cursor
        sqliteConnection = sqlite3.connect("data/events.db")
        cursor = sqliteConnection.cursor()
        return cursor, sqliteConnection
 
    # Handle errors
    except sqlite3.Error as error:
        print('Error occurred - ', error)
 
def test_luo_tietokanta(cursor):
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
 
    # Handle errors
    except sqlite3.Error as error:
        print('Error occurred - ', error)
    
    # # Close DB Connection irrespective of success
    # # or failure
    # finally:
    
    #     if sqliteConnection:
    #         sqliteConnection.close()
# test_luo_tietokanta(test_yhdista_tietokantaan()[0])  
def test_sulje_tietokanta(cursor):
    # Close the cursor
    cursor.close()

def test_lisaa_tietokantaan(event, cursor, connection):
    try:
        cursor.execute(f"""
        INSERT INTO events (summary, description, start, stop) VALUES
            ({event})""")
        connection.commit()
    except sqlite3.Error as error:
        print('Error occurred - ', error)

def test_lisaa_tietokantaantesti():
    try:
        connection = sqlite3.connect("data/events.db")
        cursor = connection.cursor()
        event = f"'testititle', 'notesdescription', '2023-08-21T00:00:00', '2023-08-21T01:00:00'"
        cursor.execute(f"""
        INSERT INTO events (summary, description, start, stop) VALUES
            ({event})""")
        connection.commit()
    except sqlite3.Error as error:
        print('Error occurred - ', error)
    
#2. Valitse oppilas
def test_valitse_oppilas(page: Page, oppilas: str):
    #valitaan oppilas
    page.locator('h1').locator('a:has-text("'+oppilas+'")').click()
    #tallennetaan url, jotta tiedetään mihin palata
    global url
    url=page.url

#3. Valitse aine
def test_jaksonopinnot(page:Page):
    #testaamiseen
    # page.locator('div[data-path="ShowPeriodCourses"]').locator("tbody").screenshot(path="screenshot.png")

    # Kouluaine
    aine= page.locator('table.index-table > tbody > tr:nth-child(1) > td > span > a').inner_text()
    #split aihe valitaan toinen osa
    aine=aine.split(":")[1]
    page.locator('table.index-table > tbody > tr:nth-child(1) > td > span > a').click()
    
    test_kotitehtavat(page, aine)
    #looppaamiseen
    #rows = page.query_selector_all(".table.index-table > tbody > tr")
    # count = 0
    # luku=0
    # for row in rows:
    #     cells = row.query_selector_all("td:first-child")
    #     count = 0
    #     for cell in cells:
    #         count = count + 1
    #         luku = luku + 1
    #         if count == 2:
    #             break
    #         # cell.screenshot(path=f"screenshot{luku}.png")
    #         cell.click()

    # #takaisin jaksonopinnoihin
    # page.goto(url)

#testataan mitä tallennettu
def test_hae_tietokantasta():
    sqliteConnection = sqlite3.connect("data/events.db")
    cursor = sqliteConnection.cursor()
    #Valitaan kaikki
    cursor.execute("SELECT * FROM events")
    rows = cursor.fetchall()
    data = []
    # Print all rows
    for row in rows:
        data.append({"summary": row[1], "description": row[2], "start": row[3], "stop": row[4], "created": row[5]})
    test_tallenna_data_tiedostoon(data, "data/new_data.txt")

#4. Hae kotitehtävät
def test_kotitehtavat(page:Page, aihe:str):
    # page.locator('table > thead > tr > th:has-text("Kotitehtävät") > tbody > td:nth-child(1)').screenshot(path="screen1.png")
    # cells = page.query_selector_all("table > thead > tr > th:has-text('Kotitehtävät') > tbody > tr")
    # Valitaan taulukko, jossa on kotitehtävät
    table = page.locator("table:has(th:has-text('Kotitehtävät'))")
    rows = table.locator("tbody tr").element_handles()
    
    # Luodaan tietokanta
    cursor, connection = test_yhdista_tietokantaan()
    test_luo_tietokanta(cursor)

    # listat
    # data = []
    # new_data = []

    # tapahtumat = test_lue_tiedosto('events.txt')
    # Create a unique identifier for the new row
    
    for row in rows:
        # Ensimmäinen solu sisältää päivämäärän
        date_str = row.query_selector("td:nth-child(1)").text_content()
        # Toinen solu sisältää kotitehtävän
        notes = row.query_selector("td:nth-child(2)").text_content()
        # Muutetaan päivämäärä oikeaan muotoon Google kalenteria varten
        date_obj = datetime.strptime(date_str, "%d.%m.%Y")
        start = date_obj.isoformat()
        # Luodaan loppuaika, joka on yksi tunti alkamisen jälkeen
        yksitunti = date_obj + timedelta(hours=1)
        stop = yksitunti.isoformat()
        # Luodaan json josta tunnistetaan onko tehtävä jo olemassa jatkossa
        # uusi_tapahtuma = {
        #     "summary": aihe,
        #     "description": notes,
        #     "start": start,
        #     "stop": stop
        # }
        uusi_tapahtuma = f"'{aihe}', '{notes}', '{start}', '{stop}'"
        test_lisaa_tietokantaan(uusi_tapahtuma, cursor, connection)
    test_hae_tietokantasta()
    test_sulje_tietokanta(cursor)
    # # Tarkista, onko uusi tapahtuma jo listassa
    #     if checkIfNameExists(tapahtumat, uusi_tapahtuma) != True:
    #         new_data.append(uusi_tapahtuma)
    #         # event.append(uusi_tapahtuma)
    
    #     # Lisätään listaan TÄMÄ VOIDAAN POISTAA
    #     data.append({"title": aihe, "due": start, "notes": notes})
        
    # # Kirjoitetaan data tiedostoon
    # test_tallenna_data_tiedostoon(data, "data/output.txt")
    # # test_tallenna_data_tiedostoon(event, "data/events.txt")
    # test_tallenna_data_tiedostoon(new_data, "data/new_data.txt")

# def checkIfNameExists(fileData, newEntry):
#     for entry in fileData:
#         if(entry["description"] == newEntry["description"] and
#             entry["summary"] == newEntry["summary"] and
#             entry["start"] == newEntry["start"] and
#             entry["stop"] == newEntry["stop"]):
#             return False
#     return True

#tallennetaan data tiedostoon
def test_tallenna_data_tiedostoon(data, file_name):
    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def test_lue_tiedosto(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    
# Read existing data from the file
existing_data = test_lue_tiedosto('events.json')  

#1. Kirjaudu sisään
def test_kirjaudu(page: Page):
    page.goto(login_url)
    page.locator('#login-frontdoor').fill(login)
    page.locator("#password").fill(password)
    page.locator('input:has-text("Kirjaudu sisään")').click()
    test_valitse_oppilas(page, wilma_person)
    test_jaksonopinnot(page)
