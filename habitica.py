
import requests
import json

# .env tiedostosta
import os
from dotenv import load_dotenv
load_dotenv()

habitica_api_user = os.environ["HABITICA_API_USER"]
habitica_api_key = os.environ["HABITICA_API_KEY"]
habitica_client = os.environ["HABITICA_CLIENT"]
habitica_challenge= os.environ["HABITICA_CHALLENGE1"]

# Yhden tehtävän lisäämiseen
def create_habitica_task(challenge_id, task_data):
    try:
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
def create_all_habitica_tasks(challenge_id, tasks):
    results = []

    for task in tasks:
        try:
            response = create_habitica_task(challenge_id, task)
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
    tasks=load_from_json('data\kotitehtavat.json')
    results = create_all_habitica_tasks(habitica_challenge, tasks)
    print(results)

if __name__ == "__main__":
  main()