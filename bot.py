import os
import subprocess
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Directory for storing audio files
AUDIO_DIR = "audio"
#WHISPER_MODEL = "whisper.cpp/models/ggml-tiny.bin"  # Using tiny model
WHISPER_MODEL = "whisper.cpp/models/ggml-small.bin"  # Using small model

# Ensure the directory exists
os.makedirs(AUDIO_DIR, exist_ok=True)

# Load bot token from a file
TOKEN_FILE = "bot_token.txt"
if not os.path.exists(TOKEN_FILE):
    raise FileNotFoundError(f"Token file '{TOKEN_FILE}' not found.")
with open(TOKEN_FILE, "r") as f:
    TOKEN = f.read().strip()

# Function to transcribe audio
def transcribe_audio(audio_path):
    wav_path = audio_path.replace(".mp3", ".wav")
    
    # Convert MP3 to WAV
    subprocess.run(["ffmpeg", "-i", audio_path, "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", wav_path], check=True)
    
    logger.info("Starting transcription...")
    
    # Run Whisper.cpp
    # ./build/bin/whisper-cli -m models/ggml-tiny.bin -f samples/jfk.wav
    # ./whisper.cpp/build/bin/whisper-cli -m whisper.cpp/models/ggml-tiny.bin -f audio/sample.wav -l uk
    result = subprocess.run(["./whisper.cpp/build/bin/whisper-cli", "-m", WHISPER_MODEL, "-f", wav_path, "-l", "uk"], capture_output=True, text=True)
    logger.info(f"Transcription result: {result}")
    
    return result.stdout.strip()

# Function to handle incoming audio files
async def handle_audio(update: Update, context: CallbackContext) -> None:
    file = update.message.voice or update.message.audio
    if not file:
   await update.message.reply_text("Надішліть голосове або аудіофайл у MP3.")
        return
    
    file_obj = await file.get_file()
    file_path = os.path.join(AUDIO_DIR, f"{file.file_id}.mp3")
    await file_obj.download_to_drive(custom_path=file_path)
    
   await update.message.reply_text("Обробляю... Це може зайняти деякий час.")
    
    try:
        text = transcribe_audio(file_path)
        await update.message.reply_text(f"Розпізнаний текст:\n{text}")
    except Exception as e:
        await update.message.reply_text("Сталася помилка при обробці аудіо.")
        logger.error(f"Помилка: {e}")

# Function for /start command
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Привіт! Надішліть MP3 або голосове повідомлення для розпізнавання.")

# Main function to run the bot
def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_audio))
    
    print("Bot is running!")
    app.run_polling()

if __name__ == "__main__":
    main()
