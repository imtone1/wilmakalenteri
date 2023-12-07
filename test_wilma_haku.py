#Playwright
from playwright.sync_api import Page
import json
# config.py
from config import login_url, login, password, wilma_person
from datetime import datetime

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

#4. Hae kotitehtävät
def test_kotitehtavat(page:Page, aihe:str):
    # page.locator('table > thead > tr > th:has-text("Kotitehtävät") > tbody > td:nth-child(1)').screenshot(path="screen1.png")
    # cells = page.query_selector_all("table > thead > tr > th:has-text('Kotitehtävät') > tbody > tr")
    # Valitaan taulukko, jossa on kotitehtävät
    table = page.locator("table:has(th:has-text('Kotitehtävät'))")
    rows = table.locator("tbody tr").element_handles()
    # rows = page.locator("table.table.allow-printlink.datatable.gridtable tbody tr").element_handles()

    # listat
    data = []
    event = []
    new_data = []

        # Create a set of unique identifiers from existing data
    existing_identifiers = {f"{item['due']}_{item['title']}" for item in existing_data}
    # Create a unique identifier for the new row
    
    for row in rows:
        # Ensimmäinen solu sisältää päivämäärän
        date_str = row.query_selector("td:nth-child(1)").text_content()
        # Toinen solu sisältää kotitehtävän
        notes = row.query_selector("td:nth-child(2)").text_content()
        # Muutetaan päivämäärä oikeaan muotoon Google kalenteria varten
        date_obj = datetime.strptime(date_str, "%d.%m.%Y")
        due_date = date_obj.isoformat()

        # Luodaan id josta tunnistetaan onko tehtävä jo olemassa jatkossa
        new_id = f"{due_date}_{notes}"

    # Jos tätä id:tä ei ole vielä olemassa, lisätään se dataan
        if new_id not in existing_identifiers:
            new_data.append({"start": due_date, "description": notes})
            event.append({"summary": aihe, "start": due_date, "description": notes})
        
        # Lisätään listaan TÄMÄ VOIDAAN POISTAA
        data.append({"title": aihe, "due": due_date, "notes": notes})

    # Kirjoitetaan data tiedostoon
    test_tallenna_data_tiedostoon(data, "output.txt")
    test_tallenna_data_tiedostoon(event, "events.txt")

#tallennetaan data tiedostoon
def test_tallenna_data_tiedostoon(data, file_name):
    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def test_lue_vanha_data(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    
# Read existing data from the file
existing_data = test_lue_vanha_data('event.json')  

#1. Kirjaudu sisään
def test_kirjaudu(page: Page):
    page.goto(login_url)
    page.locator('#login-frontdoor').fill(login)
    page.locator("#password").fill(password)
    page.locator('input:has-text("Kirjaudu sisään")').click()
    test_valitse_oppilas(page, wilma_person)
    test_jaksonopinnot(page) 