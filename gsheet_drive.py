
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime

PARENT_FOLDER_NAME = "Luma Events Master"
PARENT_FOLDER_ID = None  

# Social media base URLs
SOCIAL_LINKS = {
    'twitter': 'https://twitter.com/',
    'instagram': 'https://instagram.com/',
    'linkedin': 'https://linkedin.com/in/',
    'youtube': 'https://youtube.com/@',
    'tiktok': 'https://tiktok.com/@'
}

def create_drive_service():
    """Create and return Google Drive service with full permissions"""
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "credentials.json",
        scopes=[
            "https://www.googleapis.com/auth/drive",
            "https://spreadsheets.google.com/feeds"
        ]
    )
    return build("drive", "v3", credentials=creds)

def create_folder(service, folder_name=None):
    """Maintained for backward compatibility - uses the parent folder"""
    global PARENT_FOLDER_ID
    if not PARENT_FOLDER_ID:
        get_or_create_parent_folder(service)
    return PARENT_FOLDER_ID

def get_or_create_parent_folder(service):
    """Get or create the parent folder and make it public"""
    global PARENT_FOLDER_ID
    
    # Try to find existing parent folder
    
    query = f"name='{PARENT_FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])
    
    if items:
        PARENT_FOLDER_ID = items[0]['id']
        print(f"Using existing parent folder: {PARENT_FOLDER_NAME}")
    else:
        # Create new parent folder
        file_metadata = {
            'name': PARENT_FOLDER_NAME,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = service.files().create(body=file_metadata, fields='id').execute()
        PARENT_FOLDER_ID = folder.get('id')
        print(f" Created new parent folder: {PARENT_FOLDER_NAME}")
    
    # Make folder public (anyone with link can view)
    permission = {
        'type': 'anyone',
        'role': 'writer'  
    }
    service.permissions().create(
        fileId=PARENT_FOLDER_ID,
        body=permission,
        fields='id'
    ).execute()
    
    # Print public folder URL
    folder_url = f"https://drive.google.com/drive/folders/{PARENT_FOLDER_ID}"
    print(f"🔗 Public Folder Link: {folder_url}")
    
    return PARENT_FOLDER_ID

def create_sheet_in_folder(sheet_name, folder_id, event_details):
    """Maintained for backward compatibility - creates public event sheet"""
    return create_event_sheet(event_details)

def create_event_sheet(event_details):
    """Create a new public sheet for an event in the parent folder"""
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "credentials.json",
        scopes=[
            "https://www.googleapis.com/auth/drive",
            "https://spreadsheets.google.com/feeds"
        ]
    )
    gc = gspread.authorize(creds)
    drive_service = create_drive_service()
    
    if not PARENT_FOLDER_ID:
        get_or_create_parent_folder(drive_service)
    
    # Create spreadsheet with event name
    spreadsheet_title = f"Luma Event - {event_details['event_name']}"
    spreadsheet = gc.create(spreadsheet_title)
    
    # Move to parent folder
    drive_service.files().update(
        fileId=spreadsheet.id,
        addParents=PARENT_FOLDER_ID,
        removeParents="root",
        fields="id, parents"
    ).execute()
    
    permission = {
        'type': 'anyone',
        'role': 'writer'  
    }
    drive_service.permissions().create(
        fileId=spreadsheet.id,
        body=permission,
        fields='id'
    ).execute()
    
    # Format the sheet
    worksheet = spreadsheet.sheet1
    worksheet.update_title(event_details['event_name'][:100])  
    
    sheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet.id}"
    print(f"🔗 Public Sheet Link: {sheet_url}")
    return worksheet

def format_social_links(social_data):
    """Convert usernames to full URLs"""
    formatted = {}
    for platform, value in social_data.items():
        if value and value != 'N/A':
            base_url = SOCIAL_LINKS.get(platform, '')
            if base_url:
                if platform == 'linkedin' and not value.startswith('/in/'):
                    value = f'/in/{value.lstrip("/")}'
                formatted[platform] = f"{base_url}{value.lstrip('@')}"
            else:
                formatted[platform] = value
        else:
            formatted[platform] = 'N/A'
    return formatted

def write_attendees(sheet, event_details):
    """Write event details and attendees to the sheet"""
    # Clear existing data
    sheet.clear()
    
    headers = [
        "Username", "Full Name", "Display Name", "Bio", "Location", 
        "Website", "Profile Image URL", 
        "Twitter URL", "Instagram URL", "LinkedIn URL",
        "YouTube URL", "TikTok URL"
    ]
    
    # Format the data rows with only the fields we want
    formatted_rows = []
    for attendee in event_details['attendees']:
  
        row = attendee[:7] + attendee[10:13] + attendee[14:16]
        
        socials = {
            'twitter': row[7], 'instagram': row[8], 'linkedin': row[9],
            'youtube': row[10], 'tiktok': row[11]
        }
        formatted_socials = format_social_links(socials)
        row[7] = formatted_socials['twitter']
        row[8] = formatted_socials['instagram']
        row[9] = formatted_socials['linkedin']
        row[10] = formatted_socials['youtube']
        row[11] = formatted_socials['tiktok']
        formatted_rows.append(row)
   
    metadata = [
        ["Event Name", event_details['event_name'], "Date", event_details['event_date']],
        ["Event Time", event_details['event_time'], "Location", event_details['event_location']],
        ["Last Updated", datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "Attendees", len(event_details['attendees'])],
        [],  
        headers  # Header row
    ]
    
    sheet.update('A1', metadata)
    if formatted_rows:
        sheet.append_rows(formatted_rows)
    
   
    sheet.format("A1:D3", {
        "textFormat": {"bold": True},
        "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9}
    })
    
    sheet.format("A5:L5", {  
        "textFormat": {"bold": True},
        "backgroundColor": {"red": 0.95, "green": 0.95, "blue": 0.95}
    })
    
    # Freeze only the header row (row 5) and first column
    sheet.freeze(rows=5, cols=1)
    
    # Auto-resize columns
    sheet.columns_auto_resize(0, len(headers))
    
    print(f" Successfully wrote event details and {len(formatted_rows)} attendees")