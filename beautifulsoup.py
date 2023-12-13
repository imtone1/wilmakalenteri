# .env tiedostosta
import os
from dotenv import load_dotenv

from bs4 import BeautifulSoup as bs
import requests

import json
from datetime import datetime, timedelta, timezone

from pymongo import MongoClient

calendarID = os.environ["CALENDAR_FAMILY"]

#Google API
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import time

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

load_dotenv()
WILMA_STUDENT = os.environ["WILMA_STUDENT"]

#Wilmaan kirjautuminen ja oppilaan hakeminen
def wilma_student(login_req, session, wilma_student=WILMA_STUDENT):
    soup = bs(login_req.text, 'html.parser')
    # print(soup)
    # Etsitään linkki, joka sisältää oppilaan nimen
    oppilas_link = soup.find('a', string=wilma_student)
    if oppilas_link:
        # Linkki
        oppilas_url = oppilas_link['href']
        return session, oppilas_url
    else:
        print("There is no such student.")

def wilma_subject(session, oppilas_url):
    # Siirrytään oppilaan sivulle
    oppilaansivu=session.get(os.environ["WILMA_URL"] + oppilas_url)

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
                links.append(link_text)
                wilma_homeworks(session, link_url, link_text)
    print(f"Links: {links}")

def wilma_homeworks(session, link_url, subject_text):

     #mongoDB
    db = connect_mongodb("kotitehtavat")
    
    created = datetime.now(tz=timezone.utc)

    # Siirrytään aineen sivulle
    kotitehtavasivu=session.get(os.environ["WILMA_URL"] + link_url)
    
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

                print(f"Date: {start}, Notes: {description}")
                
                start_obj = datetime.strptime(start, "%d.%m.%Y")
                start_aamu = start_obj + timedelta(hours=1)
                start = start_aamu.isoformat()
                # Luodaan loppuaika, joka on yksi tunti alkamisen jälkeen
                yksitunti = start_aamu + timedelta(hours=2)
                stop = yksitunti.isoformat()
                subject=subject_text
                add_unique_item_mongodb(subject, description, start, stop, created, db)
                task_data=refactor_to_habitica_tasks(subject, description, start)
                count=count+1
                if count>10:
                    #odota 30 sekuntia, jotta Habitica ei rajoita liikaa (max 30 requests in a minute)
                    print("Waiting 30 seconds...")
                    count=0
                    time.sleep(30)
                create_habitica_task(task_data)

    else:
        print("Table with 'Kotitehtävät' not found or no tbody.")

#Wilman kokeiden haku sekä tallennus tietokantaan
def wilma_exams(session, oppilas_url):
        #mongoDB
        kokeet_db = connect_mongodb("kokeet")
        created = datetime.now(tz=timezone.utc)
        # Siirrytään oppilaiden kokeiden sivulle
        oppilaansivu=session.get(os.environ["WILMA_URL"] + oppilas_url+"/exams/calendar")
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
            # Luodaan loppuaika, joka on yksi tunti alkamisen jälkeen
            yksitunti = start_aamu + timedelta(hours=1)
            stop = yksitunti.isoformat()

            add_unique_item_mongodb(subject, description, start, stop, created, kokeet_db)
           
def add_unique_item_mongodb(subject, description, start, stop, created, db):
    doc = {
        "summary": subject,
        "description": description,
        'start': {
            'dateTime': start,
            'timeZone': "Europe/Helsinki",
        },
        'end': {
            'dateTime': stop,
            'timeZone': "Europe/Helsinki",
        },
        'created': created
        }
    
    # Tarkistetaan, onko samanlainen dokumentti jo olemassa
    exists = db.find_one({"summary": doc["summary"], "description": doc["description"]})

    if not exists:
        # Jos samanlaista dokumenttia ei löydy, lisätään se kokoelmaan
        lisatty=db.insert_one(doc).inserted_id
        print(f"Document added {lisatty}")
    else:
        print("Document already exists")


#kirjautuu wilmaan
def wilma_signin():
    login_url = os.environ["WILMA_URL"]
    login = os.environ["WILMA_LOGIN"]
    password = os.environ["WILMA_PASSWORD"]
    URL = login_url
    LOGIN_ROUTE = '/login'
    HEADERS = {'origin': URL, 'referer': URL + LOGIN_ROUTE}
    #jos ei toimi, käytä tätä
    # HEADERS = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36', 'origin': URL, 'referer': URL + LOGIN_ROUTE}
    session = requests.session()
    cookie_token = session.get(URL).cookies['Wilma2LoginID']
    login_payload = {
            'Login': login,
            'Password': password, 
            'SESSIONID': cookie_token
            }
    login_req = session.post(URL + LOGIN_ROUTE, headers=HEADERS, data=login_payload)
    #jos statuskoodi on 200, niin kirjautuminen onnistui
    print(f"Wilma login status code: {login_req.status_code}")
    #tallennetaan varmuuden vuoksi
    cookies = login_req.cookies

    return login_req, session

#yhdistää tietokantaan ja palauttaa kokoelman
def connect_mongodb(collection):
    #mongoDB
    atlas_uri = os.environ["ATLAS_URI"]
    client = MongoClient(atlas_uri)
    db = client["wilma"]
    collection_db = db[collection]

    return collection_db

#löytää dokumentit tietokannasta
def find_items_mongodb(collection, query={}):

    documents = collection.find(query)

    return documents

#palauttaa refaktoroidun listan google kalenteriin vietäväksi
#Käytännössä poistetaan created
def refactor_events(events):
    events_list = []

    for doc in events:
        #muotoillaan
        event = {
            "summary": doc["summary"],
            "description": doc["description"],
            "start": {
                "dateTime": doc["start"]["dateTime"],
                'timeZone': "Europe/Helsinki"
            },
            "end": {
                "dateTime": doc["end"]["dateTime"],
                'timeZone': "Europe/Helsinki"
            }
        }

        print(event)

        #lisätään listaan
        events_list.append(event)
    return events_list

#Muotoillaan tehtävä Habiticaan sopivaksi
def refactor_to_habitica_tasks(text, notes, date):
    task= {
      "type": "todo",
      "text": text,
      "notes": notes,
      "priority": "0.1",
      "date": date
    }
    return task

#Kirjautuminen Googlen kalenteriin
def google_calendar_token():
    """Tokens Google API
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
      creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
      if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
      else:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES
        )
        creds = flow.run_local_server(port=0)
      # Save the credentials for the next run
      with open("token.json", "w") as token:
        token.write(creds.to_json())
    # Call the Calendar API
    service = build("calendar", "v3", credentials=creds)

    return service

def show_calendar_events(calendarID="primary"):
    try:
        service = google_calendar_token()
       
        now = datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
        print("Getting the upcoming 10 events")
        events_result = (
                service.events()
                .list(
                    calendarId=calendarID,
                    timeMin=now,
                    maxResults=10,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
            return

            # Prints the start and name of the next 10 events
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(start, event["summary"])

    except HttpError as error:
        print(f"An error occurred in Google Calendar showing event: {error}")

#luo kalenteritapahtuman
def create_calendar_event(event, calendarID):
  service = google_calendar_token()
  event = service.events().insert(calendarId=calendarID, body=event).execute()
  print(f"Event created: {event.get('htmlLink')}")

# Yhden tehtävän lisäämiseen
def create_habitica_task(task_data, challenge_id=os.environ["HABITICA_CHALLENGE1"] ):
    try:
        habitica_api_user = os.environ["HABITICA_API_USER"]
        habitica_api_key = os.environ["HABITICA_API_KEY"]
        habitica_client = os.environ["HABITICA_CLIENT"]

        response = requests.post(
            f'https://habitica.com/api/v3/tasks/challenge/{challenge_id}',
            headers={
                'Content-Type': 'application/json',
                'x-api-user': habitica_api_user,
                'x-api-key': habitica_api_key,
                'x-client': habitica_client
            },
            # data=json.dumps(task_data)
            json=task_data
        )
        response.raise_for_status()
        return response
    except requests.RequestException as error:
        print('Habiticaan ei voitu lisätä tehtävä.', error)
        raise

# Useamman tehtävän lisäämiseen
def create_all_habitica_tasks(tasks, challenge_id=os.environ["HABITICA_CHALLENGE1"]):
    results = []

    for task in tasks:
        try:
            response = create_habitica_task( task, challenge_id)
            #json muodossa, jos jälkikäteen käytetään johonkin
            results.append({'success': True, 'response': response, 'data': task })
        except Exception as error:
            results.append({'success': False, 'error': str(error),  'data': task})

    return results

# Tehtävien lataamiseen tiedostosta. Huom! json-muoto
def load_from_json(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        tasks = json.load(file)
    return tasks

def main():
    #wilma_exams(*wilma_student(*wilma_signin()))
    wilma_subject(*wilma_student(*wilma_signin()))

    one_minute_ago = datetime.now() - timedelta(hours=30, minutes=1)
    query = {"created": {"$gte": one_minute_ago}}
    
    # show_calendar_events(calendarID)
    events=find_items_mongodb(connect_mongodb("kokeet"), query)
    refaktoroitu=refactor_events(events)
    for doc in refaktoroitu:
        create_calendar_event(doc, calendarID)
    
    tasks=load_from_json('data\kotitehtavat.json')
    habitica_challenge= os.environ["HABITICA_CHALLENGE1"]
    results = create_all_habitica_tasks( tasks, habitica_challenge)
    print(results)

if __name__ == "__main__":
  main()