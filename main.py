from bs4 import BeautifulSoup as bs
import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import time
import os

SDK_URL = None # REPLACE WITH PATH TO CREDENTIALS (EXAMPLE: C:\\Users\\You\\Desktop\\...\\SDK.json)
DB_URL = None # REPLACE WITH YOUR DATABASE URL

# Initialize Firebase Admin
cred = credentials.Certificate(SDK_URL)
firebase_admin.initialize_app(cred, {
    'databaseURL': DB_URL
})

url = 'https://www.bajasae.net/res/EventResults.aspx?competitionid=9e449a5d-e709-42e7-91ee-3b5af2eaf60c&eventkey=OVR'
school = 'Western University'

while True:
    # re-download the results every loop, otherwise the placement never changes
    placement = None
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
    except requests.RequestException as e:
        print(f"Couldn't reach results page: {e}")
        time.sleep(10)
        continue

    soup = bs(res.content, 'html.parser')
    tbody = soup.find('tbody')
    rows = tbody.find_all('tr') if tbody else []

    for row in rows:
        columns = row.find_all('td')
        if len(columns) < 3:
            continue  # skip header/spacer rows
        if columns[2].text.strip() == school:
            placement = columns[0].text.strip()
            break

    if placement:
        # Prepare the data to send
        data = {'placement': placement}
        # Reference to the Firebase Database path for the placement
        ref = db.reference('/')
        # Updating the placement at the root of the database
        ref.update(data)
        print(f"Placement data for {school} has been updated in Firebase.")
    else:
        print(f"Could not find placement data for {school}.")
    
    time.sleep(10)