import discord
import json
import ocr
import os
from groq import Groq
import sheets
from datetime import datetime, timedelta
import pytz

# Load configuration from environment variables (Railway) or config.json (local)
BOT_TOKEN = os.getenv('BOT_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')

# Load codes_channels from config.json (or empty list if not exists)
if os.path.exists('config.json'):
    with open('config.json', 'r') as f:
        config = json.load(f)
    codes_channels = config.get('codes_channels', [])
    # Use config.json values as fallback if env vars not set
    if not BOT_TOKEN:
        BOT_TOKEN = config.get('bot_token')
    if not GROQ_API_KEY:
        GROQ_API_KEY = config.get('groq_api_key')
    if not SPREADSHEET_ID:
        SPREADSHEET_ID = config.get('spreadsheet_id')
else:
    config = {'codes_channels': []}
    codes_channels = []

# Define the bot's intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# Create a bot instance
bot = discord.Client(intents=intents)

def save_config():
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    if message.content.startswith('!schedule'):
        est = pytz.timezone('America/New_York')
        now = datetime.now(est)
        days_until_monday = (7 - now.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        
        next_monday =  now + timedelta(days=days_until_monday)
        for i in range(7):
            current_day = next_monday + timedelta(days=i)
            day_name = current_day.strftime('%A')
            date_str = current_day.strftime('%b %-d')

            # Create timestamps for 8pm and 10pm ET
            time_8pm = current_day.replace(hour=20, minute=0, second=0, microsecond=0)
            time_10pm = current_day.replace(hour=22, minute=0, second=0, microsecond=0)
            
            # Convert to Unix timestamps
            timestamp_8pm = int(time_8pm.timestamp())
            timestamp_10pm = int(time_10pm.timestamp())
            
            schedule_msg = await message.channel.send(f"{day_name} {date_str}\n<t:{timestamp_8pm}:t>\n<t:{timestamp_10pm}:t>")
            await schedule_msg.add_reaction('1️⃣')
            await schedule_msg.add_reaction('2️⃣')


        
        # await message.channel.send("schedule")
    # Command to set the current channel as a codes channel
    if message.content.startswith('!setcodeschannel'):
        if (message.author.guild_permissions.manage_guild or message.author.id == message.guild.owner_id):
            if message.channel.id not in codes_channels:
                codes_channels.append(message.channel.id)
                config['codes_channels'] = codes_channels
                save_config()
                await message.channel.send(f'Channel #{message.channel.name} has been marked as a codes channel.')
            else:
                await message.channel.send(f'Channel #{message.channel.name} is already a codes channel.')
        else:
            await message.channel.send('You must be an administrator to use this command.')
        return

    # Command to unset the current channel as a codes channel
    if message.content.startswith('!unsetcodeschannel'):
        if (message.author.guild_permissions.manage_guild or message.author.id == message.guild.owner_id):
            if message.channel.id in codes_channels:
                codes_channels.remove(message.channel.id)
                config['codes_channels'] = codes_channels
                save_config()
                await message.channel.send(f'Channel #{message.channel.name} has been removed from the codes channels.')
            else:
                await message.channel.send(f'Channel #{message.channel.name} is not a codes channel.')
        else:
            await message.channel.send('You must be an administrator to use this command.')
        return

    # Check if the message is in a codes channel and has an image
    if message.channel.id in codes_channels and message.attachments:
        for attachment in message.attachments:
            if attachment.content_type.startswith('image/'):
                # Download the image
                image_path = f'temp_{attachment.filename}'
                await attachment.save(image_path)
                
                # Process the image using Groq Vision
                map_code_mapping = ocr.get_codes_from_image_groq(image_path, GROQ_API_KEY)
                
                # Delete the temporary image file
                os.remove(image_path)

                if map_code_mapping:
                    response = ""
                    sheet_data = []
                    
                    # Get current date in MST
                    mst = pytz.timezone('America/Phoenix')
                    current_date = datetime.now(mst).strftime('%m/%d/%Y')

                    for ow_map in map_code_mapping:
                        response += ow_map["map"] + " - " + ow_map["replay_code"] + " - " + ow_map["result"] + "\n"
                        # Format: Date, Map, Result, Replay Code
                        sheet_data.append([current_date, ow_map["map"], ow_map["result"], ow_map["replay_code"]])

                    if response:
                        await message.channel.send(response)
                        try:
                            sheets.update_sheet(SPREADSHEET_ID, sheet_data)
                            await message.channel.send('Spreadsheet updated successfully.')
                        except Exception as e:
                            await message.channel.send(f'Failed to update spreadsheet: {e}')
                else:
                    await message.channel.send('Could not extract any codes from the image.')

# Run the bot
if __name__ == "__main__":
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("Please replace 'YOUR_BOT_TOKEN_HERE' in config.json with your bot token.")
    elif GROQ_API_KEY == "YOUR_GROQ_API_KEY_HERE":
        print("Please replace 'YOUR_GROQ_API_KEY_HERE' in config.json with your Groq API key.")
    else:
        bot.run(BOT_TOKEN)