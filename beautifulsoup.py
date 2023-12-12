# .env tiedostosta
import os
from dotenv import load_dotenv

from bs4 import BeautifulSoup as bs
import requests

# import json
from datetime import datetime, timedelta, timezone

from pymongo import MongoClient

calendarID = os.environ["CALENDAR_FAMILY"]

#Google API
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

load_dotenv()

def wilma_exams(login_req, session):
    wilma_student = os.environ["WILMA_STUDENT"]

    #mongoDB
    kokeet_db = connect_mongodb("kokeet")

    created = datetime.now(tz=timezone.utc)


    soup = bs(login_req.text, 'html.parser')
    # print(soup)
    # Etsitään linkki, joka sisältää oppilaan nimen
    oppilas_link = soup.find('a', string=wilma_student)
    if oppilas_link:
        # Linkki
        oppilas_url = oppilas_link['href']
        # Siirrytään oppilaan sivulle
        oppilaansivu=session.get(os.environ["WILMA_URL"] + oppilas_url+"/exams/calendar")
        soup=bs(oppilaansivu.text, 'html.parser')
        tables = soup.select('#main-content .table')

        # data = []

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
            start_aamu = start_obj + timedelta(hours=6)
            start = start_aamu.isoformat()
            # Luodaan loppuaika, joka on yksi tunti alkamisen jälkeen
            yksitunti = start_obj + timedelta(hours=1)
            stop = yksitunti.isoformat()
                
            koe = {
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
            
            # data.append(koe)
            # post_id = kokeet_db.insert_one(koe).inserted_id
            # post_id
            # Tarkistetaan, onko samanlainen dokumentti jo olemassa
            exists = kokeet_db.find_one({"summary": koe["summary"], "description": koe["description"]})

            if not exists:
                # Jos samanlaista dokumenttia ei löydy, lisätään se kokoelmaan
                kokeet_db.insert_one(koe)
                print("Document added")
            else:
                print("Document already exists")

        #     # Muunnetaan datetime-objektit
        #     start_iso = start.isoformat() if isinstance(start, datetime) else start
        #     stop_iso = stop.isoformat() if isinstance(stop, datetime) else stop
        #     created_iso = created.isoformat() if isinstance(created, datetime) else created

        #     data = []
        #     koe1 = {
        #         "summary": subject,
        #         "description": description,
        #         'start': {
        #             'dateTime': start_iso,
        #             'timeZone': "Europe/Helsinki",
        #         },
        #         'end': {
        #             'dateTime': stop_iso,
        #             'timeZone': "Europe/Helsinki",
        #         },
        #         'created': created_iso
        #     }
        #     data.append(koe1)
        # # JSON-muotoon
        # json_data = json.dumps(data, indent=4, ensure_ascii=False)
        # print(json_data)

    else:
        print("There is no such student.")

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

def connect_mongodb(collection):
    #mongoDB
    atlas_uri = os.environ["ATLAS_URI"]
    client = MongoClient(atlas_uri)
    db = client["wilma"]
    kokeet_db = db[collection]
    return kokeet_db

def get_items_mongodb(collection, query={}):

    documents = collection.find(query)
    print(f"Result for your query {query} is: ")
    for doc in documents:
        print(doc)

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

def main():
    # wilma_exams(*wilma_signin())
    # one_minute_ago = datetime.now() - timedelta(hours=10, minutes=1)
    # query = {"created": {"$gte": one_minute_ago}}

    # get_items_mongodb(connect_mongodb("kokeet"), query)
    show_calendar_events(calendarID)

if __name__ == "__main__":
  main()