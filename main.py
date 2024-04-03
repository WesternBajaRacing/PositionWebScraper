from bs4 import BeautifulSoup as bs
import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import time
import os

SDK_URL = none # REPLACE WITH PATH TO CREDENTIALS (EXAMPLE: C:\\Users\\You\\Desktop\\...\\SDK.json)
DB_URL = none # REPLACE WITH YOUR DATABASE URL

# Initialize Firebase Admin
cred = credentials.Certificate(SDK_URL)
firebase_admin.initialize_app(cred, {
    'databaseURL': DB_URL
})

url = 'https://www.bajasae.net/res/EventResults.aspx?competitionid=9e449a5d-e709-42e7-91ee-3b5af2eaf60c&eventkey=OVR'
res = requests.get(url)
soup = bs(res.content, 'html.parser')
rows = soup.find('tbody').find_all('tr')
school = 'Western University'
placement = None

while true:
    for row in rows:
        if row.find_all('td')[2].text.strip() == school:
            placement = row.find_all('td')[0].text.strip()
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