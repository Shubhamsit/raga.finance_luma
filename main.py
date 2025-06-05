
import os
from scrape_attendees import scrape_attendees
from luma_scraper import login_to_luma
from gsheet_drive import create_drive_service, create_folder, create_sheet_in_folder, write_attendees
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()



event_url ="https://lu.ma/alteverything?tk=HbYCNm" 
# event_url ="https://lu.ma/bemo?tk=bEHY5D" 

# event_url = os.environ.get("EVENT_URL")
event_type = "past"
# event_type = os.environ.get("EVENT_TYPE")


def extract_event_id(luma_url):
    path = urlparse(luma_url).path 
    return path.strip('/')

event_id = extract_event_id(event_url)
print(event_id) 


if __name__ == "__main__":
  
    driver=login_to_luma()



    # obj = scrape_attendees(driver,event_url,)
    obj = scrape_attendees(driver,event_id,event_type)
    attendees=obj['attendees']

    print("hello")
    

    if attendees:
        # Step 2: Create Drive folder and sheet

        folder_service = create_drive_service()
        folder_id = create_folder(folder_service, "Raga Leads Folder")

        if folder_id:
            sheet = create_sheet_in_folder("Web3_Leads", folder_id,obj)

            # Step 3: Write attendees
            
            write_attendees(sheet,obj)
    else:
        print("No attendees scraped.")


