import gspread
from google.oauth2.service_account import Credentials

# Service account credentials never expire
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'service-account.json'

def get_creds():
    """Get credentials from service account file.
    Service account credentials don't expire and are ideal for bots.
    """
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )
    return creds

def update_sheet(spreadsheet_id, data):
    """
    Appends data to a worksheet in the spreadsheet.
    """
    creds = get_creds()
    client = gspread.authorize(creds)
    
    # Open the spreadsheet
    spreadsheet = client.open_by_key(spreadsheet_id)
    
    # You can select a worksheet by title. 
    # For example, to select a worksheet named "Sheet1":
    # worksheet = spreadsheet.worksheet("Sheet1")
    # By default, it will select the first visible sheet
    worksheet = spreadsheet.worksheet("Robot Input")

    # Check if sheet has data
    if worksheet.get_all_values():
        worksheet.append_row([]) # Add an empty row for a gap

    # Append data to the worksheet
    worksheet.append_rows(data)
    print(f"Successfully updated spreadsheet.")

if __name__ == '__main__':
    # Example usage:
    # This will append two rows to the spreadsheet.
    # Replace with your spreadsheet ID and data.
    SPREADSHEET_ID = '1k_xPfP2QvzdYrbvBPrxgqNGa2kTUB4Gg01V7Bj131wM'
    SAMPLE_DATA = [
        ['Player1', '12345'],
        ['Player2', '67890']
    ]
    update_sheet(SPREADSHEET_ID, SAMPLE_DATA)
