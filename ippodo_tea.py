"""
Product Availability Checker for *Ippodo Tea* website
    - This script scrapes the Ippodo Tea product page to check for stock availability
    - Sends an email notification when the item is back in stock
"""

import re
import unicodedata
import requests
import smtplib
import os
import logging
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from email.mime.text import MIMEText

# Load environment variables from .env file
load_dotenv()

# Constants for stock status
IN_STOCK_TEXT = os.environ.get("IPPODO_IN_STOCK_TEXT", "Add to bag")
SOLD_OUT_TEXT = os.environ.get("IPPODO_SOLD_OUT_TEXT", "Sold Out")
ELEMENT_TO_FIND = os.environ.get("IPPODO_ELEMENT_TO_FIND", "span")
CLASS_TO_FIND = os.environ.get("IPPODO_CLASS_TO_FIND", "product-stock-status")

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL")

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler("ippodo_tracker.log"),
        logging.StreamHandler()
    ]
)

def norm_text(s: str) -> str:
    # strip leading/trailing, collapse internal whitespace, normalize unicode, and lowercase
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"\s+", " ", s.strip())
    return s

# List of Products to Track
PRODUCTS_TO_TRACK = [
    {
        "name": "Ummon (40g Can)",
        "url": "https://ippodotea.com/collections/matcha/products/ummon-no-mukashi-40g"
    },
    {
        "name": "Ummon (40g Bag)",
        "url": "https://ippodotea.com/collections/matcha/products/ummon-40g-bag"
    }
]

"""
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
response = requests.get(PRODUCTS_TO_TRACK[1]["url"], headers=headers)
response.raise_for_status()

soup = BeautifulSoup(response.content, 'html.parser')
status_element = soup.find(ELEMENT_TO_FIND, class_=CLASS_TO_FIND)
"""

def check_stock(product):
    """Checks a single product page to see if the item is in stock."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(product["url"], headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        # Find the specific element defined for this product
        status_element = soup.find(ELEMENT_TO_FIND, class_=CLASS_TO_FIND)

        if status_element:
            if SOLD_OUT_TEXT == status_element.text or SOLD_OUT_TEXT.lower() == norm_text(status_element.text).lower():
                return "Out of Stock"
            elif IN_STOCK_TEXT.lower() == norm_text(status_element.text).lower():
                return "In Stock"
            else:
                return "Error"
        else:
            # If the element isn't found, it might mean the page layout changed,
            # or the item is available (e.g., the "sold out" div disappears).
            # We'll log a warning.
            logging.warning(f"Status element not found for {product['name']}.")
            return "Out Of Stock"

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching webpage for {product['name']}: {e}")
        return "Error"
    except Exception as e:
        logging.error(f"An unexpected error occurred for {product['name']}: {e}")
        return "Error"


def send_notification_email(product):
    """Sends an email for a specific product that is back in stock."""
    if not SENDER_EMAIL or not SENDER_PASSWORD or not RECIPIENT_EMAIL:
        logging.error("Email credentials not found in environment variables.")
        return

    logging.info(f"Item '{product['name']}' is in stock! Preparing to send email notification...")
    subject = f"In Stock Alert: {product['name']}"
    body = (f"The product you are tracking is now back in stock!\n\n"
            f"Product: {product['name']}\n"
            f"Buy it here: {product['url']}")

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        logging.info("Email notification sent successfully!")
        server.quit()
    except Exception as e:
        logging.error(f"Failed to send email: {e}")


if __name__ == "__main__":
    for product in PRODUCTS_TO_TRACK:
        logging.info("\n\n--- CHECK START ---")
        status = check_stock(product)

        # Log in the requested format
        logging.info(f"name of product: {product['name']}")
        logging.info(f"link: {product['url']}")
        logging.info(f"status: {status}")
        logging.info("--- CHECK END ---")

        if "In Stock" in status:
            send_notification_email(product)