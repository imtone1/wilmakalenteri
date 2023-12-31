#muuttjat
from muuttujat import *

#Web scraping
from bs4 import BeautifulSoup as bs
import requests

#datetime
from datetime import datetime, timedelta

#kirjautuu wilmaan
def wilma_signin():
    '''Kirjautuu Wilmaan ja palauttaa kirjautumisen sekä sessionin'''

    login_url = WILMA_URL
    login = WILMA_LOGIN
    password = WILMA_PASSWORD
    URL = login_url
    login_route = LOGIN_ROUTE
    HEADERS = {'origin': URL, 'referer': URL + login_route}
    cookie=COOKIE
    #jos ei toimi, käytä tätä
    # HEADERS = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36', 'origin': URL, 'referer': URL + LOGIN_ROUTE}
    session = requests.session()
    cookie_token = session.get(URL).cookies[cookie]
    login_payload = {
            'Login': login,
            'Password': password, 
            'SESSIONID': cookie_token
            }
    login_req = session.post(URL + login_route, headers=HEADERS, data=login_payload)
    #jos statuskoodi on 200, niin kirjautuminen onnistui
    print(f"Wilma login status code: {login_req.status_code}")
    #tallennetaan varmuuden vuoksi
    cookies = login_req.cookies

    return login_req, session

#Oppilaan hakeminen Wilmasta
def wilma_student(login_req, session, wilma_student=WILMA_STUDENT):
    '''Oppilaan hakeminen Wilmasta'''

    soup = bs(login_req.text, 'html.parser')
    # print(soup)
    # Etsitään linkki, joka sisältää oppilaan nimen
    oppilas_link = soup.find('a', string=wilma_student)
    if oppilas_link:
        # Oppilaan linkki
        oppilas_url = oppilas_link['href']
        return session, oppilas_url
    else:
        print("There is no such student.")

def wilma_subject(session, oppilas_url):
    '''Siirrytään oppilaan sivulle. Haetaan oppilaan sivulta aineet sekä wilma_homeworks-funktiolla kotitehtävät'''

    oppilaansivu=session.get(WILMA_URL + oppilas_url)

    soup=bs(oppilaansivu.text, 'html.parser')
    tables = soup.select('#main-content .table', {"class": "table index-table"})

    links = []
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            link_element = row.select_one('td:nth-of-type(1) a')
            if link_element:
                link_url = link_element.get('href')
                link_text = link_element.get_text(separator=' ', strip=True)
                #links append tuple (link_url, link_text)
                links.append((link_url, link_text))
                #links.append(link_text)
                wilma_homeworks(session, link_url, link_text)
    print(f"Links: {links}")

def wilma_homeworks(session, link_url):
    '''Haetaan kotitehtävät'''
   

    # Siirrytään aineen sivulle
    kotitehtavasivu=session.get(WILMA_URL + link_url)
    
    soup=bs(kotitehtavasivu.content, 'html.parser')
    
    # Sellainen taulu, jossa on "Kotitehtävät" theadissa
    target_table = None
    for table in soup.find_all("table"):
        if table.find("thead"):
            th_elements = table.find("thead").find_all("th")
            if any("Kotitehtävät" in th.get_text() for th in th_elements):
                target_table = table
                break

    # onko tällä tbody
    if target_table and target_table.find("tbody"):
        rows = target_table.find("tbody").find_all("tr")
        count=0
        for row in rows:
            # jokaiselta riviltä haetaan solut
            cells = row.find_all("td")
            if len(cells) >= 2:
                start = cells[0].get_text(strip=True)
                description = cells[1].get_text(strip=True)
                start_obj = datetime.strptime(start, "%d.%m.%Y")
                start_aamu = start_obj + timedelta(hours=1)
                start = start_aamu.isoformat()
                print(f"Date: {start}, Notes: {description}, Start: {start}")
                          
    else:
        print("Table with 'Kotitehtävät' not found or no tbody.")

#Wilman kokeiden haku sekä tallennus tietokantaan
def wilma_exams(session, oppilas_url):
    '''Haetaan kokeet'''

    # Siirrytään oppilaiden kokeiden sivulle
    oppilaansivu=session.get(WILMA_URL + oppilas_url+"/exams/calendar")
    soup=bs(oppilaansivu.text, 'html.parser')
    tables = soup.select('#main-content .table')

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
        #ensimmäinen arvo on viikonpäivä, joten valitaan toinen
        pvm = start.split(' ')[1]
        start_obj = datetime.strptime(pvm, "%d.%m.%Y")
        start_aamu = start_obj + timedelta(hours=6)
        start = start_aamu.isoformat()
        print(f"Date: {start}, Subject: {subject}, Notes: {description}")

def main():

    # ############################################################################################################
    # #WILMA
    wilma_students = WILMA_STUDENTS
    wilma_stundent = wilma_students.split(",")
    login, session = wilma_signin()
    for student in wilma_stundent:
        print(f"Student: {student}")
        wilma_exams(*wilma_student(login, session, student))
        
        wilma_subject(*wilma_student(login, session, student))
    print("Gone through all students")

if __name__ == "__main__":
  main()