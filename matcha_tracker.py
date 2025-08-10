# Product Availability Tracker
# This script scrapes a product page to check if an item is back in stock
# and sends an email notification when it is. It also logs its activity.

# --- 1. Import Necessary Libraries ---
import requests
import smtplib
import os
import logging # <-- Import the logging library
from bs4 import BeautifulSoup
from email.mime.text import MIMEText

# --- 2. Configure Logging ---
# This sets up a logger that writes to a file named 'tracker.log'
# and also prints to the console.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("tracker.log"), # Log to a file
        logging.StreamHandler()            # Also print to console
    ]
)

# --- 3. Configuration ---
PRODUCT_URL = "https://ippodotea.com/collections/matcha/products/ummon-no-mukashi-40g"

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL")

# --- 4. The Stock Checking Function ---
def check_stock():
    """Checks the product page to see if the item is in stock."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        logging.info("Checking product page...")
        response = requests.get(PRODUCT_URL, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        buy_button = soup.find("button", class_="ProductForm__AddToCart")

        if buy_button:
            button_text = buy_button.get_text(strip=True)
            logging.info(f"Found button with text: '{button_text}'")
            return "Sold Out" not in button_text
        else:
            logging.warning("Could not find the 'Add to Cart' or 'Sold Out' button.")
            return False

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching the webpage: {e}")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred during stock check: {e}")
        return False

# --- 5. The Email Sending Function ---
def send_notification_email():
    """Sends an email to notify that the product is back in stock."""
    if not SENDER_EMAIL or not SENDER_PASSWORD or not RECIPIENT_EMAIL:
        logging.error("Email credentials (sender, password, or recipient) not found in environment variables.")
        return

    logging.info("Item is in stock! Preparing to send email notification...")
    subject = "Product In Stock Alert!"
    body = f"The product you are tracking is now back in stock!\n\nBuy it here: {PRODUCT_URL}"
    
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
    except smtplib.SMTPAuthenticationError:
        logging.error("SMTP Authentication Error. Check credentials and App Password.")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

# --- 6. Main execution block ---
if __name__ == "__main__":
    logging.info("--- Starting Product Availability Check ---")
    
    is_in_stock = check_stock()
    if is_in_stock:
        send_notification_email()
    else:
        logging.info("Item is out of stock.")
        
    logging.info("--- Check complete. ---")