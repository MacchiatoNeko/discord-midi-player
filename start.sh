#!/bin/bash
currentVer=$(python3 --version)
requiredVer="3.5.3"

if [ "$(printf '%s\n' "$requiredVer" "$currentVer" | sort -V | head -n1)" = "$requiredVer" ]; then
    python3 -m pip install --upgrade pip 2>&1 >/dev/null

    # Remove debug.json file
    rm debug.json

    # Install the requirements
    # Uncomment the command below to install from the requirements file
    python3 -m pip install -r requirements.txt 2>&1 >/dev/null

    # Finally, start the bot
    python3 Bot.py
else
    echo "## Failed to run! Make sure you have Python with a version greater than 3.5.3 ##"
fi
