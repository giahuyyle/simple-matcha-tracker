# Simple Matcha Tracker

Matcha Product Availability Tracker
This project contains a Python script that automatically monitors a product webpage to check for stock availability. When the product comes back in stock, the script sends an email notification. The entire process is automated to run on a schedule using GitHub Actions.

Features
Web Scraping: Monitors a specific product URL for changes in stock status.

Email Notifications: Sends an email alert as soon as the product is available.

Scheduled Automation: Uses GitHub Actions to run the check automatically on a recurring schedule (e.g., every hour) without needing a local machine to be running.

Secure: Uses GitHub Secrets to safely store sensitive information like email credentials, so they are never exposed in the code.

Prerequisites
Before you begin, ensure you have the following:

A GitHub account.

Python 3.x installed on your local machine (for local testing).

A Gmail account to be used for sending notifications.

Setup and Configuration
Follow these steps to set up the project.

1. Clone the Repository
First, clone this repository to your local machine:

git clone <your-repository-url>
cd <your-repository-name>

2. Install Local Dependencies
Create a virtual environment and install the required Python packages from the requirements.txt file. This is mainly for running the script locally for testing.

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt

3. Configure GitHub Secrets
For the automation to work, you must store your email credentials securely in your GitHub repository's secrets.

Navigate to your repository on GitHub.

Go to Settings > Secrets and variables > Actions.

Click New repository secret and add the following two secrets:

SENDER_EMAIL: Your full Gmail address (e.g., youremail@gmail.com).

SENDER_PASSWORD: Your 16-digit Gmail App Password.

Important: You must generate an App Password for this to work with 2-Factor Authentication. Do not use your regular account password. You can generate one here: Google Account App Passwords.

4. Customize the Script (Optional)
Product URL: Open the Python script (your_script_name.py) and change the PRODUCT_URL variable to the URL of the product you want to track.

Recipient Email: Set the RECIPIENT_EMAIL variable to the email address where you want to receive notifications.

Usage
Running Locally
You can run the script on your local machine for immediate testing. Make sure you have set the environment variables for your credentials first.

# On Linux/macOS
export SENDER_EMAIL="your_email@gmail.com"
export SENDER_PASSWORD="your_app_password"

# On Windows (Command Prompt)
set SENDER_EMAIL="your_email@gmail.com"
set SENDER_PASSWORD="your_app_password"

# Run the script
python your_script_name.py

Automation with GitHub Actions
The primary way to use this tracker is through the included GitHub Actions workflow (.github/workflows/track_product.yml).

Scheduled Runs: By default, the workflow is configured to run every hour. You can change the schedule by editing the cron expression in the .yml file.

Manual Runs: You can also trigger the workflow manually:

Go to the Actions tab in your GitHub repository.

Select the Product Stock Tracker workflow from the sidebar.

Click the Run workflow dropdown and then the Run workflow button.

The workflow will handle setting up the environment, installing dependencies, and running the script using the secrets you configured. You can view the logs from each run in the Actions tab.
