import subprocess
import os
from dotenv import load_dotenv
load_dotenv()

os.environ['PGPASSWORD'] = os.getenv("DB_PASSWORD")
sql_file_path = os.path.join(os.path.dirname(__file__), 'sql', 'create_table.sql')



subprocess.run(['psql', '-U', 'postgres', '-d', 'gmail_db', '-a', '-f', sql_file_path])

subprocess.run(['python', 'fetch_and_store_emails.py'])

subprocess.run(['python', 'process_emails.py'])


del os.environ['PGPASSWORD']

token_file = 'token.json'
if os.path.exists(token_file):
    os.remove(token_file)
