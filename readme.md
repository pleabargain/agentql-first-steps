# AgentQL First Run Scrapeme Live

A Python script that scrapes product information from scrapeme.live/shop using AgentQL and Playwright. The script collects Pokemon product data, saves it in multiple formats, and organizes everything in timestamped project folders.

## Features

- Scrapes product information (name, price, thumbnail)
- Creates organized project folders with timestamps
- Saves data in multiple formats (JSON, HTML)
- Downloads product images
- Comprehensive logging system
- Handles errors gracefully

## Project Structure

scrapeme.li_YYYYMMDD_HHMMSS/           # Main project folder
├── scrapeme.li_YYYYMMDD_HHMMSS.json   # Raw JSON data
├── scrapeme.li_YYYYMMDD_HHMMSS.html   

crapeme.li_YYYYMMDD_HHMMSS/ # Main project folder
├── scrapeme.li_YYYYMMDD_HHMMSS.json # Raw JSON data
├── scrapeme.li_YYYYMMDD_HHMMSS.html # HTML representation
└── images/ # Product images
├── Bulbasaur_001-350x350.png
├── Ivysaur_002-350x350.png
└── ...

## Requirements

- Python 3.x
- playwright
- agentql
- requests

## Installation

pip install playwright agentql requests
playwright install  # Install browser binaries

### PITA playwright
playwright was a PITA to install. It took way too long to install on my windows 11 machine.

## Usage

```bash
python agentql_first_run_scrapeme_live.py
```

## Output Files

1. **JSON File**: Raw scraped data in JSON format
   - Product names
   - Prices
   - Thumbnail URLs

2. **HTML File**: Visual representation of scraped data
   - Website info and timestamp
   - Copy of the Python script used
   - JSON data display
   - Product cards with images

3. **Image Files**: Downloaded product images
   - Named using product names
   - Original image extensions preserved

4. **Log File**: Detailed operation logs
   - Timestamps
   - Success/failure messages
   - Error details

## Functions

- `setup_logging()`: Configures logging system
- `generate_html()`: Creates HTML representation of data
- `setup_project_folders()`: Creates folder structure
- `download_images()`: Downloads product images

## Error Handling

- Logs all errors with timestamps
- Continues operation if individual image downloads fail
- Creates detailed error messages for troubleshooting

## Notes

- Script includes wait times for page loading
- Uses headless browser automation
- Creates new project folder for each run
- Maintains organized file structure

