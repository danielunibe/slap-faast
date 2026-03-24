@echo off
TITLE Slap!Faast System Core
echo [SYSTEM] Initializing Core Modules...
echo [SYSTEM] Loading Virtual Environment...

call venv\Scripts\activate

echo [SYSTEM] Launching GUI...
python -m src.integration.startup

pause
