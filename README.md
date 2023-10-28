# AnyFlipFetcher
Simple script to fetch any document from AnyFlip as PDF file.

# Requirements
This script is using selenium to drive web browser and Firefox installation is required.

# Setup
Rename `.env.template` to `.env` and enter your `firefox.exe` path for `FIREFOX_PATH` key.
Install PIP packages from `requirements.txt`.

# Usage
To use the script simply call with your desired document url and wait for the script to finish going through the whole book.
```bash
python app.py --url https://anyflip.com/abcdf/qwert
```

