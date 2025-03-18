#!/bin/bash

set -e  # Stop script on error

# Update system and install required packages
echo "🔹 Installing required packages..."
sudo apt update && sudo apt install -y git cmake build-essential ffmpeg python3-pip

# Clone Whisper.cpp repository
echo "🔹 Cloning whisper.cpp..."
git clone https://github.com/ggerganov/whisper.cpp.git || echo "Repository already exists."
cd whisper.cpp

# Compile Whisper.cpp
echo "🔹 Compiling Whisper.cpp..."
make

# Prompt user to select a model
default_model="small"
#Display available models: "
bash models/download-ggml-model.sh
read -p "Enter model name (or press Enter to use '$default_model'): " model
model=${model:-$default_model}  # Use default model if none is provided

# Download selected model
echo "🔹 Downloading model $model..."
bash models/download-ggml-model.sh $model

# Return to the original directory
cd ..

# Prepare Python environment 
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "🔹 Installing Python dependencies..."
pip3 install -r requirements.txt

# Test Whisper.cpp installation
echo "🔹 Testing Whisper.cpp..."
./whisper.cpp/build/bin/whisper-cli -m whisper.cpp/models/ggml-$model.bin -f whisper.cpp/samples/jfk.wav

echo "✅ Installation complete! Whisper is ready to use."
