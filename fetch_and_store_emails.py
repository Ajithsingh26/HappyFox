import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import googleapiclient.discovery
import psycopg2
from datetime import datetime
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)
cursor = conn.cursor()

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']
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

with googleapiclient.discovery.build('gmail', 'v1', credentials=creds) as service:
    results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
    messages = results.get('messages', [])

    for message in messages:
        msg_id = message['id']
        
        cursor.execute("SELECT COUNT(*) FROM emails WHERE message_id = %s", (msg_id,))
        count = cursor.fetchone()[0]

        if count == 0:
            msg = service.users().messages().get(userId='me', id=msg_id).execute()
            subject = next(h['value'] for h in msg['payload']['headers'] if h['name'] == 'Subject')
            sender = next(h['value'] for h in msg['payload']['headers'] if h['name'] == 'From')
            received_at = datetime.fromtimestamp(int(msg['internalDate']) / 1000.0)

            cursor.execute("INSERT INTO emails (message_id, subject, sender, message, received_at) VALUES (%s, %s, %s, %s, %s)",
                        (msg_id, subject, sender, msg['snippet'], received_at))
            conn.commit()

conn.close()
