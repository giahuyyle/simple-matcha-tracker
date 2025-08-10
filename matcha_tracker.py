# Product Availability Tracker
# This script scrapes a product page to check if an item is back in stock
# and sends an email notification when it is.

# --- 1. Import Necessary Libraries ---
import requests  # To make HTTP requests to the website
import smtplib   # To send emails
import time      # To pause the script between checks
from bs4 import BeautifulSoup # To parse the HTML of the website
from email.mime.text import MIMEText # To format the email
import os

# --- 2. Configuration ---
# IMPORTANT: Fill in these details for the script to work.

# The URL of the product you want to track
PRODUCT_URL = "https://ippodotea.com/collections/matcha/products/ummon-no-mukashi-40g"

# Email configuration
# NOTE: For security, it's highly recommended to use an "App Password" for Gmail
# instead of your regular password.
# How to get an App Password:
# 1. Go to your Google Account settings (myaccount.google.com)
# 2. Go to "Security"
# 3. Enable 2-Step Verification if it's not already on.
# 4. Under "Signing in to Google," click on "App passwords."
# 5. Generate a new password for "Mail" on "Other (Custom name)" and use that password here.
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# os.environ.get to extract Github secrets
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL")

# --- 3. The Stock Checking Function ---
def check_stock():
    """
    Checks the product page to see if the item is in stock.
    Returns True if in stock, False otherwise.
    """
    try:
        # Set a User-Agent header to mimic a real browser visit
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        # Fetch the content of the product page
        print("Checking product page...")
        response = requests.get(PRODUCT_URL, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes (like 404 or 500)

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # --- Find the Add to Cart / Sold Out button ---
        # Website structures change. If this script stops working, this is the
        # part you'll likely need to update.
        # We are looking for a button with the class 'ProductForm__AddToCart'.
        # The text inside this button tells us the stock status.
        buy_button = soup.find("button", class_="ProductForm__AddToCart")

        if buy_button:
            button_text = buy_button.get_text(strip=True)
            print(f"Found button with text: '{button_text}'")

            if "Sold Out" in button_text:
                return False  # The item is out of stock
            else:
                return True   # The item is in stock!
        else:
            print("Warning: Could not find the 'Add to Cart' or 'Sold Out' button. The website layout may have changed.")
            return False

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during stock check: {e}")
        return False

# --- 4. The Email Sending Function ---
def send_notification_email():
    """
    Sends an email to notify that the product is back in stock.
    """
    print("Item is in stock! Preparing to send email notification...")

    # Create the email message
    subject = "Product In Stock Alert!"
    body = f"The product you are tracking is now back in stock!\n\nBuy it here: {PRODUCT_URL}"
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL

    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Secure the connection
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        
        # Send the email
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        print("Email notification sent successfully!")
        
        # Disconnect from the server
        server.quit()
    except smtplib.SMTPAuthenticationError:
        print("\n--- SMTP Authentication Error ---")
        print("Failed to log in. Please check your SENDER_EMAIL and SENDER_PASSWORD.")
        print("Remember to use a Google App Password if you have 2-Factor Authentication enabled.")
    except Exception as e:
        print(f"Failed to send email: {e}")

# --- 5. The Main Loop ---
if __name__ == "__main__":
    print("--- Starting Product Availability Tracker ---")
    
    # Check for configuration
    if "your_email@gmail.com" in SENDER_EMAIL or "your_app_password" in SENDER_PASSWORD:
        print("\n!!! CONFIGURATION NEEDED !!!")
        print("Please open the script and fill in your details in the 'Configuration' section before running.")
    else:
        while True:
            is_in_stock = check_stock()
            if is_in_stock:
                send_notification_email()
                break  # Exit the script after sending the notification
            else:
                # If out of stock, wait for 1 hour before checking again.
                # You can change this value (in seconds).
                # Avoid checking too frequently to not get blocked by the website.
                print("Item is out of stock. Will check again in 1 hour.")
                time.sleep(3600) # 3600 seconds = 1 hour
