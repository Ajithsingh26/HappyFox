# Gmail API Integration Project

This project is a Python script that integrates with Gmail API to fetch and process emails based on predefined rules.

## Prerequisites

- Python 3.x installed
- A Gmail API project set up on the Google Cloud Console
- PostgreSQL database server installed
- Psql command-line tool for executing SQL scripts
- Gmail API credentials file (`credentials.json`)
- Python virtual environment (optional but recommended)

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/Ajithsingh26/HappyFox.git
    cd HappyFox
    ```

2. Create and activate a virtual environment (optional):

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: .\venv\Scripts\activate
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Set up the Gmail API credentials:

    - Follow the instructions in the [Gmail API Python Quickstart](https://developers.google.com/gmail/api/quickstart) to obtain `credentials.json`.
    - Save the `credentials.json` file in the project root directory.

5. Set up the database:
   - create a postgres database

## Usage

To run the main script which handles everything
  


1. To run the main script which handles everything:

    ```bash
    python main_script.py
    ```


## Testing

Run the unit tests to ensure the functionality of the scripts:

```bash
python unit_testing/test_fetch_and_store_emails.py
