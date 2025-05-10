The python script within this repo to scrape race statistics from the SAE website during the endurance race and send it to the firebase.

The required file to have permissions to firebase can be retriebed from firebase through:
  1. Project Settings
  2. Service Accounts
  3. Generate New Private key
  4. download the file, and place within folder with scraper python file
  5. change line 13 to the downloaded files name
  6. the script should open a window to view SAE site
  7. Mouse clicks will occur every 60 seconds to refresh the page to get to the endurance races information
