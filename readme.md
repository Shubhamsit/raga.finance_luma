# 🚀 Luma Events Automation System For Raga.finance



## 🌟 Features
- **Automatic Google Sheet Generation** from Luma events using Scraping
- **Smart Social Media Linking** (Twitter/Instagram/LinkedIn/YouTube/TikTok)


## Project Structure

```

raga.finance_luma/
├── __pycache__/            
├── venv/                     
├── .env                (need to be created)
├── credentials.json         
├── gsheet_drive.py         
├── luma_scraper.py         
├── main.py                             
|    readme.md              
├── scrape_attendees.py      

```

## 🚀 1. For Setup
###  First ` Clone the repository`

   ## -> Create `.env` file with these exact values:
   ```bash
   EMAIL="examaple@gmail.com" // change with yours luma email

   PASSWORD="luma@123dhedhe" // your actual password

   EVENT_URL="https://lu.ma/pakav9at?tk=AzhgsJ"   // just paste the event url you want to scrap
   EVENT_TYPE="upcoming"  // either upcoming or past


   ```



   ### Add `credentials.json` file  (provided / download through drive link )
   

   

## 2. Activating the Virtual Environment

Make sure you're in the project directory (`raga.finance_luma`) before running these commands.

### 🪟 On Windows (CMD)
```
venv\Scripts\activate
```

### 💻 On macOS / Linux / Windows (PowerShell)
```
source venv/bin/activate
```


## 3. Running the Project

Ensure your virtual environment is **activated** and both the `.env` and `credentials.json` files are correctly configured.

Then execute the main script:

```
python main.py
```

This script will:
- Authenticate and log into your Luma account
- Scrape attendee details from the specified event(s)
- Automatically create and populate a **Google Sheet** with the extracted data


✅ **Final Output:**  
> Once the process completes, **both the Google Sheet link and the Google Drive folder link** will be generated in the terminal. These links allow you to view and manage all the event data you’ve scraped — neatly organized and stored.



> **Note:** To avoid session timeout issues during longer scraping operations, it is recommended to increase your system’s screen timeout or sleep settings if possible
