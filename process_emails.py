import os
import json
import psycopg2
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import googleapiclient.discovery
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError

# Load rules from a JSON file
with open('rules.json', 'r') as f:
    rules = json.load(f)

load_dotenv()

conn = psycopg2.connect(
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)
cursor = conn.cursor()

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_gmail_service():
    creds = None
    try:
        creds = Credentials.from_authorized_user_file('token.json')

        if creds.expired:
            creds.refresh(Request())

    except (FileNotFoundError, RefreshError):
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return googleapiclient.discovery.build('gmail', 'v1', credentials=creds)


def create_label(service, label_name):
    labels = service.users().labels().list(userId='me').execute().get('labels', [])
    for label in labels:
        if label['name'] == label_name:
            return

    new_label = {'name': label_name, 'messageListVisibility': 'show', 'labelListVisibility': 'labelShow'}
    service.users().labels().create(userId='me', body=new_label).execute()

def get_label_id_by_name(service, label_name):
    labels = service.users().labels().list(userId='me').execute()
    for label in labels.get('labels', []):
        if label['name'] == label_name:
            return label['id']
    return None

def apply_rules(email, message_id):
    for rule in rules:
        if rule['predicate'] == 'All' and all(check_condition(email, condition) for condition in rule['conditions']):
            perform_actions(message_id, rule['actions'])
        elif rule['predicate'] == 'Any' and any(check_condition(email, condition) for condition in rule['conditions']):
            perform_actions(message_id, rule['actions'])

def check_condition(email, condition):
    field_name = condition['field']
    value = condition['value']

    if field_name == 'date received':
        current_date = datetime.now()
        threshold_date = current_date - timedelta(days=value)
        if condition['predicate'] == 'Equal to':
            return email['received_at'] == threshold_date
        elif condition['predicate'] == 'Not Equal to':
            return email['received_at'] != threshold_date
        elif condition['predicate'] == 'Less than':
            return email['received_at'] > threshold_date
        elif condition['predicate'] == 'Greater than':
            return email['received_at'] < threshold_date
        
    else:
        if condition['predicate'] == 'Contains':
            return value.lower() in email[field_name].lower()
        elif condition['predicate'] == 'Does not Contain':
            return value.lower() not in email[field_name].lower()
        elif condition['predicate'] == 'Equal to':
            return value.lower() in email[field_name].lower()
        elif condition['predicate'] == 'Not Equal to':
            return value.lower() not in email[field_name].lower()
        

def perform_actions(message_id, actions):
    service = get_gmail_service()

    for action in actions:
        if action == 'Mark as Read':
            try:
                service.users().messages().modify(userId='me', id=message_id, body={'removeLabelIds': ['UNREAD']}).execute()
            except Exception as e:
                print(f"Error modifying message: {e}")
        elif action == 'Mark as Unread':
            try:
                service.users().messages().modify(userId='me', id=message_id, body={'addLabelIds': ['UNREAD']}).execute()
            except Exception as e:
                print(f"Error modifying message: {e}")
        elif action.startswith('Move Message'):
            try:
                label_name = action.split(' ', 2)[-1]
                create_label(service, label_name)
                label_id = get_label_id_by_name(service, label_name)
                if label_id:
                    service.users().messages().modify(userId='me', id=message_id, body={'addLabelIds': [label_id]}).execute()
                else:
                    print(f"There is no Label in this name: {label_name}")
            except Exception as e:
                print(f"Error modifying message: {e}")

# Fetch emails from the database
cursor.execute("SELECT message_id, subject, sender, message, received_at FROM emails")
emails = cursor.fetchall()

for email in emails:
    email_data = {
        'subject': email[1],
        'sender': email[2],
        'message': email[3],
        'received_at': email[4],
    }
    apply_rules(email_data, email[0])

conn.close()
