import datetime
#Google API
import os.path
import json

# config.py
from config import calendarId

#Google API
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def main():
  """Tokens Google API
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.My Project 48334
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
     
  try: 
  # Call the Calendar API
    service = build("calendar", "v3", credentials=creds)
  
    try:
        show_events(service)

    except HttpError as error:
        print(f"An error occurred: {error}")
    try:
        # create_event(
        # service,
        # "Test event",
        # "This is a test event",
        # "2023-08-12"
        # )
        # Load events from file
        with open('data/new_data.txt', 'r', encoding='utf-8') as file:
            events = json.load(file)
        # Iterate over events and create them
        for event in events:
            summary = event['summary'].strip()
            description = event['description'].strip()
            start_time = event['start']
            stop_time = event['stop']
            print(summary, description, start_time, stop_time )
            # Create the event
            create_event(service, summary, description, start_time, stop_time )
       #puhdistetaan tiedosto seuraavaa kertaa varten
        with open('data/new_data.txt', 'w'):
          pass
    except HttpError as error:
        print(f"An error occurred: {error}")

  except HttpError as error:
    print(f"An error occurred in Google Calendar calling: {error}")

#creates task to google calendar "Perhe" with start and end time
# def create_event(service, summary, description, start_time, end_time):
#   event = {
#     "summary": summary,
#     "description": description,
#     "start": {
#       "dateTime": start_time,
#       "timeZone": "Europe/Helsinki",
#     },
#     "end": {
#       "dateTime": end_time,
#       "timeZone": "Europe/Helsinki",
#     },
#   }
#   event = service.events().insert(calendarId=calendarId, body=event).execute()
#   print (f"Event created: {event.get('htmlLink')}")


  #creates task to google calendar "Perhe" whole day event
def create_event(service, summary, description, start_time, stop_time):
  event = {
    "summary": summary,
    "description": description,
    'start': {
    'dateTime': start_time,
    'timeZone': "Europe/Helsinki",
    },
    'end': {
    'dateTime': stop_time,
    'timeZone': "Europe/Helsinki",
    }  
  }
  event = service.events().insert(calendarId=calendarId, body=event).execute()
  print(f"Event created: {event.get('htmlLink')}")


def show_events(service):
    # Call the Calendar API
   now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
   print("Getting the upcoming 10 events")
   events_result = (
        service.events()
        .list(
            calendarId="primary",
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

if __name__ == "__main__":
  main()