pythonVersion=$(python3 --version)
parsedVersion=$(echo $pythonVersion | sed 's/[^0-9]*//g') 

if [[ $parsedVersion -gt "352" ]];
then
    # Display Python code logs (Errors, printings, etc.)
    export PYTHONUNBUFFERED=true

    python3 -m pip install --upgrade pip 2>&1 >/dev/null

    # Install the requirements
    # Uncomment the command below to install from the requirements file
    python3 -m pip install -r req.txt 2>&1 >/dev/null

    # Finally, start the bot
    python3 Bot.py
else
    echo "## Failed to run! Make sure you have Python with a version greater than 3.5.2 ##"
fi
