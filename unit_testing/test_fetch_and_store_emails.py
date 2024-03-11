import unittest
import subprocess
import psycopg2
from dotenv import load_dotenv
import os

class TestFetchAndStoreEmails(unittest.TestCase):

    def setUp(self):
        load_dotenv()

        self.conn = psycopg2.connect(
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        self.cursor = self.conn.cursor()
        sql_file_path = os.path.join(os.path.dirname(__file__), '..', 'sql', 'create_table.sql')
        with open(sql_file_path, 'r') as sql_file:
            create_table_query = sql_file.read()
            self.cursor.execute(create_table_query)
            self.conn.commit()

    def tearDown(self):
        self.cursor.close()
        self.conn.close()

    def test_fetch_and_store_emails(self):
        subprocess.run(['python', 'fetch_and_store_emails.py'])

        self.cursor.execute("SELECT COUNT(*) FROM emails")
        result = self.cursor.fetchone()[0]

        self.assertGreater(result, 0, "Number of emails in the database doesn't match the expected count")

if __name__ == '__main__':
    unittest.main()
