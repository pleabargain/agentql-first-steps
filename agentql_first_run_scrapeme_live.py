import agentql
from playwright.sync_api import sync_playwright
import json
from datetime import datetime
import logging
from urllib.parse import urlparse
import os
import requests
import shutil

def setup_logging():
    """
    Configure and initialize the logging system for the scraper.
    
    Sets up logging to both file and console with the following configuration:
    - Log Level: INFO
    - Format: timestamp - log level - message
    - Output: Both 'scraping.log' file and console output
    - File Handler: Appends to 'scraping.log'
    - Stream Handler: Prints to console
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('scraping.log'),
            logging.StreamHandler()
        ]
    )

def generate_html(data, filename, script_content, domain, timestamp):
    """
    Generate an HTML file from the scraped product data.
    
    Args:
        data (dict): Dictionary containing product information
        filename (str): Path where the HTML file will be saved
        script_content (str): Content of the Python script
        domain (str): Domain name of scraped website
        timestamp (str): Timestamp of the scrape
    
    Creates an HTML file with:
    - H1 header with website name and timestamp
    - Python script in code block
    - JSON data in code block
    - Product cards with name, price, and thumbnail
    """
    try:
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Scraped Data</title>
            <style>
                .product { margin: 20px; padding: 10px; border: 1px solid #ddd; }
                img { max-width: 200px; }
                code { 
                    display: block;
                    white-space: pre-wrap;
                    background-color: #f4f4f4;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 5px;
                }
            </style>
        </head>
        <body>
        """
        
        # Add website name and timestamp as H1
        html_content += f"<h1>Website: {domain} - Scraped at: {timestamp}</h1>"
        
        # Add Python script
        html_content += "<h2>Python Script Used:</h2>"
        html_content += f"<code>{script_content}</code><br>"
        
        # Add JSON data
        html_content += "<h2>Scraped JSON Data:</h2>"
        html_content += f"<code>{json.dumps(data, indent=4)}</code><br>"
        
        # Add products
        html_content += "<h2>Products:</h2>"
        for product in data['products']:
            html_content += f"""
            <div class="product">
                <h2>{product['name']}</h2>
                <p>Price: {product['price']}</p>
                <img src="{product['thumbnail']}" alt="{product['name']}">
            </div>
            """
        
        html_content += "</body></html>"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logging.info(f"HTML file generated: {filename}")
    except Exception as e:
        logging.error(f"Error generating HTML: {str(e)}")

def setup_project_folders(domain, timestamp):
    """
    Create and setup the project folder structure for the current scraping run.
    
    Args:
        domain (str): First 10 characters of the website domain
        timestamp (str): Current timestamp in format YYYYMMDD_HHMMSS
    
    Returns:
        tuple: (base_folder, images_folder)
            - base_folder (str): Path to main project folder
            - images_folder (str): Path to images subfolder
    
    Creates folder structure:
    domain_timestamp/
    └── images/
    
    Raises:
        Exception: If folder creation fails
    """
    try:
        base_folder = f"{domain}_{timestamp}"
        images_folder = os.path.join(base_folder, "images")
        
        os.makedirs(base_folder, exist_ok=True)
        os.makedirs(images_folder, exist_ok=True)
        
        logging.info(f"Created project folders: {base_folder}")
        return base_folder, images_folder
    except Exception as e:
        logging.error(f"Error creating project folders: {str(e)}")
        raise

def download_images(data, images_folder):
    """
    Download and save product images from the scraped data.
    
    Args:
        data (dict): Dictionary containing product information with structure:
            {
                'products': [
                    {
                        'name': str,
                        'price': float,
                        'thumbnail': str (URL)
                    },
                    ...
                ]
            }
        images_folder (str): Path to folder where images will be saved
    
    For each product:
    1. Cleans product name for use in filename
    2. Downloads image from thumbnail URL
    3. Saves image with format: ProductName_original-image-name.ext
    
    Handles errors:
    - Individual image download failures
    - Network issues
    - File writing problems
    
    Logs:
    - Successful downloads with product name and filename
    - Failed downloads with error details
    - General function errors
    """
    try:
        for idx, product in enumerate(data['products']):
            try:
                image_url = product['thumbnail']
                clean_name = ''.join(c if c.isalnum() else '_' for c in product['name'])
                original_filename = os.path.basename(image_url)
                image_name = f"{clean_name}_{original_filename}"
                image_path = os.path.join(images_folder, image_name)
                
                response = requests.get(image_url, stream=True)
                if response.status_code == 200:
                    with open(image_path, 'wb') as f:
                        response.raw.decode_content = True
                        shutil.copyfileobj(response.raw, f)
                    logging.info(f"Downloaded image: {image_name} for product: {product['name']}")
                else:
                    logging.error(f"Failed to download image: {image_url} for product: {product['name']}")
            except Exception as e:
                logging.error(f"Error processing image for product {product['name']}: {str(e)}")
                
    except Exception as e:
        logging.error(f"Error in download_images function: {str(e)}")

try:
    # Initialize logging system
    setup_logging()
    
    with sync_playwright() as playwright, playwright.chromium.launch(headless=False) as browser:
        # Initialize browser and create new page with AgentQL wrapper
        page = agentql.wrap(browser.new_page())
        page.goto("https://scrapeme.live/shop/")
        
        # Explicit wait for page loading
        print("Waiting 3 seconds for page to load completely...")
        logging.info("Waiting 3 seconds for page to load completely...")
        page.wait_for_timeout(3000)  # 3000ms = 3 seconds
        
        # Wait for complete page load
        page.wait_for_load_state("networkidle")    # No network activity for 500ms
        page.wait_for_load_state("domcontentloaded")  # DOM fully loaded
        logging.info("Page loaded successfully")
        
        # Define query for product data
        QUERY = """
        {
            products[] {
                name
                price
                thumbnail
            }
        }
        """

        # Execute query and get response
        response = page.query_data(QUERY)
        
        # Setup folder structure for current run
        domain = urlparse("https://scrapeme.live/shop/").netloc[:10]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_folder, images_folder = setup_project_folders(domain, timestamp)
        
        # Save scraped data as JSON
        json_filename = os.path.join(project_folder, f"{domain}_{timestamp}.json")
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(response, f, indent=4)
        logging.info(f"JSON file saved: {json_filename}")
        
        # Get the content of the current script
        with open(__file__, 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        # Generate HTML representation
        html_filename = os.path.join(project_folder, f"{domain}_{timestamp}.html")
        generate_html(response, html_filename, script_content, domain, timestamp)
        
        # Download product images
        download_images(response, images_folder)
        
except Exception as e:
    logging.error(f"An error occurred: {str(e)}")