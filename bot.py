import whisper
import subprocess
import os
import logging
import requests
import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import torch

available_models = whisper.available_models()
print(f"Available models: {available_models}")

# Directory for storing audio files
AUDIO_DIR = "audio"
MODEL = "small"

THREADS = 8  # Number of threads for Whisper.cpp
torch.set_num_threads(THREADS)

# Load model once at startup
model = whisper.load_model(MODEL, device = "cpu")

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DB_FILE = "bot_data.db"

def init_db():
    """Initialize the SQLite database and create the necessary table."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER PRIMARY KEY,
            alias TEXT,
            request_count INTEGER DEFAULT 0,
            last_request TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_chat_id_to_db(chat_id):
    """Save chat_id to the database if it doesn't already exist and update request info."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO users (chat_id, alias, request_count, last_request) 
            VALUES (?, ?, 0, NULL)
        """, (chat_id, None))
        cursor.execute("""
            UPDATE users 
            SET request_count = request_count + 1, 
                last_request = datetime('now') 
            WHERE chat_id = ?
        """, (chat_id,))
        conn.commit()
        conn.close()
        logger.info(f"Saved or updated chat ID in database: {chat_id}")
    except Exception as e:
        logger.error(f"Error saving or updating chat ID in database: {e}")

# Modify the save_chat_id function to use the updated database logic
def save_chat_id(chat_id):
    save_chat_id_to_db(chat_id)

# Ensure the directory exists
os.makedirs(AUDIO_DIR, exist_ok=True)

# Load bot token from a file
TOKEN_FILE = "bot_token.txt"
if not os.path.exists(TOKEN_FILE):
    raise FileNotFoundError(f"Token file '{TOKEN_FILE}' not found.")
with open(TOKEN_FILE, "r") as f:
    TOKEN = f.read().strip()

# Secondary bot details
SECONDARY_BOT_API = "http://192.168.0.101:5000/processAudio"  # Replace <SECONDARY_BOT_IP> with the actual IP

# Function to transcribe audio locally
def transcribe_audio(file_path):
    # Convert MP3 to WAV
    wav_path = file_path.replace(".mp3", ".wav")

    print(f"wav_path = {wav_path}")
    # subprocess.run(["ffmpeg", "-i", file_path, "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", wav_path], check=True)

    # result = subprocess.run(
    #     ["./whisper.cpp/build/bin/whisper-cli",
    #       "--model", "/whisper.cpp/models/ggml-small.bin", 
    #       "--file", wav_path,
    #       "--no-timestamps", "true",
    #       "--language", "uk",
    #       "--threads", THREADS], capture_output=True, text=True)

    """Transcribe audio using the preloaded Whisper model"""
    result = model.transcribe(file_path, language="uk")
    return result["text"]

# Function to forward request to another bot and retrieve its response
def forward_to_secondary_bot(file_path, chat_id=None):
    try:
        with open(file_path, "rb") as audio_file:
            files = {"audio": audio_file}
            print("Запит")
            response = requests.post(SECONDARY_BOT_API, files=files)

        if response.status_code == 200:
            json_response = response.json()
            return json_response.get("text", None)  # Extract the transcribed text
        else:
            logger.warning(f"Secondary bot error: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error forwarding to secondary bot: {e}")
        return None


# Telegram bot handler for audio files
async def handle_audio(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    save_chat_id(chat_id)  # Save or update chat ID in the database

    file = update.message.voice or update.message.audio
    if not file:
        await update.message.reply_text("Надішліть голосове або аудіофайл у MP3.")
        return

    file_obj = await file.get_file()
    file_path = os.path.join(AUDIO_DIR, f"{file.file_id}.mp3")
    await file_obj.download_to_drive(custom_path=file_path)

    await update.message.reply_text("Обробляю... Це може зайняти деякий час.")
    
    # Try forwarding to the secondary bot first
    transcribed_text = forward_to_secondary_bot(file_path, chat_id)
    if transcribed_text is not None:  # Only proceed if the secondary bot fails
        await send_long_message(chat_id, f"Розпізнано вторинним ботом:\n{transcribed_text}", context)
        return
    
    # If the secondary bot fails, process locally
    try:
        text = transcribe_audio(file_path)
        await send_long_message(chat_id, f"Розпізнаний текст:\n{text}", context)
    except Exception as e:
        await update.message.reply_text("Сталася помилка під час розпізнавання аудіо.")
        logger.error(f"Помилка: {e}")

async def send_long_message(chat_id, text, context):
    max_length = 4096
    for i in range(0, len(text), max_length):
        await context.bot.send_message(chat_id=chat_id, text=text[i:i + max_length])

# Function for /start command
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Привіт! Надішліть MP3 або голосове повідомлення для розпізнавання.")

# Main function to run the bot
def main():
    init_db()  # Initialize the database
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO | filters.ATTACHMENT, handle_audio))
    
    print("Bot is running!")
    app.run_polling()

if __name__ == "__main__":
    main()