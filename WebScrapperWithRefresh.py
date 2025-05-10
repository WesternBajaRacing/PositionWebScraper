from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import time
import os

SDK_URL = "baja-dash-firebase-adminsdk-9aob2-98f962df3c.json" # REPLACE WITH PATH TO CREDENTIALS (EXAMPLE: C:\\Users\\You\\Desktop\\...\\SDK.json)
DB_URL = "https://baja-dash-default-rtdb.firebaseio.com" # REPLACE WITH YOUR DATABASE URL

# Initialize Firebase Admin
cred = credentials.Certificate(SDK_URL)
firebase_admin.initialize_app(cred, {
    'databaseURL': DB_URL
})

url = 'https://results.bajasae.net/Leaderboard.aspx'

# Use Selenium to load the page and wait for it to render
driver = webdriver.Chrome()
driver.get(url)
time.sleep(5)  # Adjust the wait time as needed

school = 'Western University'       #check to make sure this matches the bold label for our team on their site
placement = None

repeat = True
last_lap_milis = 0

while repeat:

    # Extract the HTML content after the page is loaded
    html_content = driver.page_source
    soup = bs(html_content, 'html.parser')

    # Wait for the dropdown element to be clickable
    dropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'MainContent_DropDownListEvents'))
    )

    # Click on the dropdown to open it
    dropdown.click()

    # Select an option from the dropdown
    select = Select(dropdown)
    select.select_by_visible_text('Endurance')  # Change 'Design' to the option you want to select

    # Click on the "Show Most Recent Results" button
    button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'MainContent_ButtonLookupEvent'))
    )
    button.click()
    # Wait for the page to load the new content
    time.sleep(5)  # delay to ensure the tables are retrieved from the endurance page

    # Extract the HTML content after the page is loaded
    html_content2 = driver.page_source
    soup2 = bs(html_content2, 'html.parser')

    # Find the table rows
    table_rows = soup2.find_all('tr')

    # Extract data from the table
    for row in table_rows[1:]:  # Skip the first row as it contains header information
        columns = row.find_all('td')
        if len(columns) < 6:
            continue  # Skip rows that don't have enough columns
        if columns[2].contents[1].contents[0] == school:
            placement = columns[0].text.strip()
            laps = columns[3].text.strip()  # Total laps
            
            last_lap = columns[4].next_sibling.contents[1].contents[0]  # Last lap time
            best_lap = str(columns[5].next_sibling.contents[1].contents[0]) + " " + str(columns[5].next_sibling.contents[3].contents[0]) # Best lap time
            #value to hold last_lap as miliseconds when formatted as MM:ss.sss
            # Find the colon and period positions
                
            colon_pos = last_lap.index(":")  # Now you can find the position of the colon   
            dot_pos = last_lap.index(".")    # Find the position of the dot

            # Extract minutes, seconds, and milliseconds
            minutes = int(last_lap[:colon_pos])                    # Extract minutes (before colon)
            seconds = int(last_lap[colon_pos+1:dot_pos])           # Extract seconds (between colon and period)
            milliseconds = int(last_lap[dot_pos+1:])               # Extract milliseconds (after period)

                # Convert everything to milliseconds
            last_lap_milis = minutes * 60000 + seconds * 1000 + milliseconds
            #print(f"last_lap in milliseconds: {last_lap_milis}") # Print the last lap time in milliseconds

            if(int(placement) == 1):        #if the car is in first place, there is no car ahead
                print("No team ahead.")     
                target = "WE IN FIRST!!!!!!!"               #set theses to -1 so wix doesnt break when they are None
                theirLaps = "N/A"            #will need to add a catch on wix for when these are -1 that is doesnt show anything
                theirTime = "N/A"
                theirNumber = "N/A"
                break

            # Find the data for the team ahead by comparing team names
            target_row = None
            for row in table_rows[1:]:          #loops through all cars to determine the car ahead
                otherColumns = row.find_all('td')       #finds all the data seen on screen for the car
                if len(otherColumns) < 7:       #if the car has no data, skip it
                    continue
                team_position = otherColumns[0].text.strip()        #finds the position of the car of this loop
                if int(team_position) == int(placement)-1:          #ends if the position is equal to ours, so the last update of target_row is ahead of us
                    
                    target_row = row
                    break  # Stop iterating if the target team is found

            if target_row:
                target = otherColumns[2].contents[1].contents  # Find the name of team in front
                theirLaps = otherColumns[3].text.strip()  # Find the laps of the team ahead of the target team
                theirTime = otherColumns[4].next_sibling.contents[1].contents[0]  # Find the time of the team ahead of the target team
                theirNumber = otherColumns[1].text.strip()  # Find the number of the team ahead of the target team
                
                #print(f"Team Ahead: {target}, Their Laps: {theirLaps}, Their Time: {theirTime}")
            break

    if placement:
        # Prepare the data to send
        placementData = {'placement': placement}        #seting up key values for sendin to firebase
        lapsData = {'laps': laps}
        lastLapData = {'lastLap': last_lap}
        bestLapData = {'bestLap': best_lap}
        carAheadData = {'carAhead': theirTime}
        targetData = {'target': target}
        lapsAheadData = {'lapsAhead': theirLaps}
        carAheadNumber = {'carAheadNumber': theirNumber}
        last_lap_milis = {'previousLapTime': last_lap_milis}

        # Reference to the Firebase Database path for the placement
        ref = db.reference('/scraped/')
        # Updating the placement at the root of the database
        ref.update(placementData)               #sending data to firebase
        ref.update(lapsData)
        ref.update(lastLapData)
        ref.update(bestLapData)
        ref.update(targetData)
        ref.update(carAheadData)
        ref.update(lapsAheadData)
        ref.update(carAheadNumber)
        ref.update(last_lap_milis)
        print(f"Placement data for {school} has been updated in Firebase.")
    else:
        print(f"Could not find placement data for {school}.")
        
    time.sleep(10)                  #delay for new refresh of leaderboard
     # Refresh the page to get the latest data
    driver.refresh()

# Close the browser
driver.quit()
