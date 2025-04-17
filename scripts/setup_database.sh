#!/bin/bash

DB_FILE="../bot_data.db"

# Check if SQLite3 is installed
if ! command -v sqlite3 &> /dev/null; then
    echo "SQLite3 is not installed. Installing..."
    sudo apt update
    sudo apt install -y sqlite3
else
    echo "SQLite3 is already installed."
fi

# Check if the database file exists
if [ ! -f "$DB_FILE" ]; then
    echo "Database file not found. Creating a new database..."
    sqlite3 "$DB_FILE" <<EOF
CREATE TABLE IF NOT EXISTS users (
    chat_id INTEGER PRIMARY KEY,
    alias TEXT,
    request_count INTEGER DEFAULT 0,
    last_request TEXT
);
EOF
    echo "Database initialized successfully."
else
    echo "Database file already exists."
fi

# Open the database in SQLite3 shell
echo "Opening the database..."
sqlite3 "$DB_FILE"
