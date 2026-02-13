# OCR Discord Bot

Discord bot that extracts Overwatch replay codes from screenshots and logs them to Google Sheets.

## Features
- OCR using Groq Vision API
- Automatic Google Sheets logging
- Schedule management with Discord timestamps

## Local Setup

1. Clone the repository
2. Copy `config.example.json` to `config.json` and fill in your values
3. Download your Google Cloud service account JSON and save as `service-account.json`
4. Install dependencies: `pip install -r requirements.txt`
5. Run: `python bot.py`

## Railway Deployment

### Environment Variables
Set these in Railway dashboard:

- `BOT_TOKEN` - Your Discord bot token
- `GROQ_API_KEY` - Your Groq API key
- `SPREADSHEET_ID` - Your Google Spreadsheet ID
- `GOOGLE_SERVICE_ACCOUNT_JSON` - Paste the entire contents of your `service-account.json` file

### Deploy
1. Connect your GitHub repository to Railway
2. Set the environment variables above
3. Railway will auto-deploy on push

## Commands
- `!setcodeschannel` - Mark current channel for OCR processing (admin only)
- `!unsetcodeschannel` - Unmark current channel (admin only)
- `!schedule` - Generate a weekly schedule with reaction options
