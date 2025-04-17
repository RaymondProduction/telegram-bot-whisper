import whisper
from flask import Flask, request, jsonify
import os
import torch
import logging
import json

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration from JSON file
CONFIG_FILE = "config.json"
if not os.path.exists(CONFIG_FILE):
    raise FileNotFoundError(f"Configuration file '{CONFIG_FILE}' not found.")
with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

# Use settings from the configuration
SECOND_BOT_CONFIG = config["secondBot"]
MODEL = SECOND_BOT_CONFIG["model"]
AUDIO_DIR = SECOND_BOT_CONFIG["audio"]["dir"]
THREADS = SECOND_BOT_CONFIG["threads"]
DEVICE = SECOND_BOT_CONFIG["device"]
PORT = SECOND_BOT_CONFIG["port"]
HOST = SECOND_BOT_CONFIG["host"]

torch.set_num_threads(THREADS)
model = whisper.load_model(MODEL, device=DEVICE)

# Ensure the directory exists
os.makedirs(AUDIO_DIR, exist_ok=True)

# Initialize Flask app
app = Flask(__name__)

# Function to transcribe audio locally
def transcribe_audio(file_path):
    # Convert MP3 to WAV
    #wav_path = audio_path.replace(".mp3", ".wav")
    #subprocess.run(["ffmpeg", "-i", audio_path, "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", wav_path], check=True)

    # result = subprocess.run(
    #     ["./whisper.cpp/build/bin/whisper-cli",
    #       "--model", WHISPER_MODEL, 
    #       "--file", wav_path,
    #       "--no-timestamps", "true",
    #       "--language", "uk",
    #       "--threads", THREADS], capture_output=True, text=True)

    """Transcribe audio using the preloaded Whisper model"""
    result = model.transcribe(file_path, language="uk")
    return result["text"]

# HTTP endpoint to process audio
@app.route('/processAudio', methods=['POST'])
def process_audio():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio']
    file_path = os.path.join(AUDIO_DIR, audio_file.filename)
    audio_file.save(file_path)

    try:
        # Transcribe the audio file
        text = transcribe_audio(file_path)
        return jsonify({"text": text}), 200
    except Exception as e:
        logger.error(f"Error processing audio: {e}")
        return jsonify({"error": "Failed to process audio"}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(host=HOST, port=PORT)
