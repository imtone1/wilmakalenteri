# .env tiedostosta
import os
from dotenv import load_dotenv

from bs4 import BeautifulSoup as bs
import requests

import json
from datetime import datetime, timedelta

load_dotenv()

def test_kirjaudu():
    login_url = os.environ["WILMA_URL"]
    login = os.environ["WILMA_LOGIN"]
    password = os.environ["WILMA_PASSWORD"]
    wilma_student = os.environ["WILMA_STUDENT"]


    URL = login_url
    LOGIN_ROUTE = '/login'
    HEADERS = {'origin': URL, 'referer': URL + LOGIN_ROUTE}
    #jos ei toimi, käytä tätä
    # HEADERS = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36', 'origin': URL, 'referer': URL + LOGIN_ROUTE}
    s = requests.session()
    cookie_token = s.get(URL).cookies['Wilma2LoginID']
    login_payload = {
            'Login': login,
            'Password': password, 
            'SESSIONID': cookie_token
            }
    login_req = s.post(URL + LOGIN_ROUTE, headers=HEADERS, data=login_payload)
    #jos statuskoodi on 200, niin kirjautuminen onnistui
    print(login_req.status_code)
    #tallennetaan varmuuden vuoksi
    cookies = login_req.cookies
    # soup = bs(s.get(URL + 'watchlist').text, 'html.parser')
    # tbody = soup.find('table', id='companies')
    soup = bs(login_req.text, 'html.parser')
    # print(soup)
    # Etsitään linkki, joka sisältää oppilaan nimen
    oppilas_link = soup.find('a', string=wilma_student)
    if oppilas_link:
        # Linkki
        oppilas_url = oppilas_link['href']
        # Siirrytään oppilaan sivulle
        oppilaansivu=s.get(os.environ["WILMA_URL"] + oppilas_url+"/exams/calendar")
        soup=bs(oppilaansivu.text, 'html.parser')
        # print(soup)
        # kokeet = soup.find('main', id="main-content").findAll('table')
        # print(kokeet)
        # print(kokeet.text)
        # kokeet1 = soup.find('a', string="Kokeet")
        # print(kokeet1)
        tables = soup.select('#main-content .table')

        data = []

        for table in tables:
            row = table.find_all('tr')
            start = row[0].select_one('td:nth-of-type(1) strong').text
            subject = row[0].select_one('td:nth-of-type(2)').text
            description = row[2].select_one('td').text
            subject_strip = subject.strip()
            subject_list = subject_strip.split('\r\n')
            # Valitaan splitatusta arvot
            # print(subject_list)
            subject = subject_list[0].strip() + subject_list[1].strip() + subject_list[2].strip()
            pvm = start.split(' ')[1]
            start_obj = datetime.strptime(pvm, "%d.%m.%Y")
            start = start_obj.isoformat()
            # Luodaan loppuaika, joka on yksi tunti alkamisen jälkeen
            yksitunti = start_obj + timedelta(hours=1)
            stop = yksitunti.isoformat()

            data.append({
                "summary": subject,
                "description": description,
                'start': {
                'dateTime': start,
                'timeZone': "Europe/Helsinki",
                },
                'end': {
                'dateTime': stop,
                'timeZone': "Europe/Helsinki",
                } })

        # Muuntaa kerätyt tiedot JSON-muotoon
        json_data = json.dumps(data, indent=4, ensure_ascii=False)

        # Tulostaa JSON-muotoiset tiedot
        print(json_data)


    else:
        print("Oppilasta ei löytynyt")

# Käyttöesimerkki
test_kirjaudu()

