# Product Availability Tracker (Multi-Item Version)
# This script scrapes a list of product pages to check for stock availability
# and sends an email notification when an item is back in stock.

# --- 1. Import Necessary Libraries ---
import requests
import smtplib
import os
import logging
from bs4 import BeautifulSoup
from email.mime.text import MIMEText

# --- 2. Configure Logging ---
# This sets up a logger that writes to a file named 'tracker.log'
# and also prints to the console. The format is simplified for clarity.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler("tracker.log"),
        logging.StreamHandler()
    ]
)

# --- 3. Configuration ---
# --- List of Products to Track ---
# Each product is a dictionary with:
# - name: The product name for logs and emails.
# - url: The full URL of the product page.
# - find_element: The HTML tag to look for (e.g., 'button', 'div').
# - find_class: The CSS class of the element.
# - sold_out_text: The text inside the element that indicates it's sold out.
PRODUCTS_TO_TRACK = [
    {
        "name": "Ippodo - Ummon-no-mukashi",
        "url": "https://ippodotea.com/collections/matcha/products/ummon-no-mukashi-40g",
        "find_element": "button",
        "find_class": "ProductForm__AddToCart",
        "sold_out_text": "Sold Out"
    },
    {
        "name": "Marukyu Koyamaen - Enshuryu School Favored Matcha Ichigen no Shiro",
        "url": "https://www.marukyu-koyamaen.co.jp/english/shop/products/1143020c1-1143200c1",
        "find_element": "div",
        "find_class": "stock_message_box",
        "sold_out_text": "Sorry, this item is currently sold out."
    },
    {
        "name": "Ippodo - Sayaka-no-mukashi",
        "url": "https://global.ippodo-tea.co.jp/collections/matcha/products/matcha103644",
        "find_element": "button",
        "find_class": "product-form--add-to-cart-button",
        "sold_out_text": "Sold out"
    }
]

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL")

# --- 4. The Stock Checking Function ---
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
        status_element = soup.find(product["find_element"], class_=product["find_class"])

        if status_element:
            element_text = status_element.get_text(strip=True)
            if product["sold_out_text"] in element_text:
                return "Out of Stock"
            else:
                return "In Stock"
        else:
            # If the element isn't found, it might mean the page layout changed,
            # or the item is available (e.g., the "sold out" div disappears).
            # We'll assume it's in stock but log a warning.
            logging.warning(f"Status element not found for {product['name']}. Assuming it's in stock.")
            return "In Stock (Element Not Found)"

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching webpage for {product['name']}: {e}")
        return "Error"
    except Exception as e:
        logging.error(f"An unexpected error occurred for {product['name']}: {e}")
        return "Error"

# --- 5. The Email Sending Function ---
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

# --- 6. Main execution block ---
if __name__ == "__main__":
    logging.info("--- CHECK START ---")

    for product in PRODUCTS_TO_TRACK:
        status = check_stock(product)
        # Log in the requested format
        logging.info(f"name of product: {product['name']}")
        logging.info(f"link: {product['url']}")
        logging.info(f"status: {status}")

        if "In Stock" in status:
            send_notification_email(product)

    logging.info("--- CHECK END ---")