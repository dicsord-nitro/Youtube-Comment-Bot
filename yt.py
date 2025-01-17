import os
import random
import logging
import asyncio
import aiohttp
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from bs4 import BeautifulSoup
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
from time import sleep

# Load environment variables from a .env file
load_dotenv()

# Configuration
CLIENT_SECRETS_FILE = os.getenv("CLIENT_SECRETS_FILE", "client_secret.json")
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
KEYWORDS_FILE = os.getenv("KEYWORDS_FILE", 'data/keywords.txt')
COMMENTS_FILE = os.getenv("COMMENTS_FILE", 'data/comments.txt')
LINKS_FILE = os.getenv("LINKS_FILE", 'data/links.txt')
PROXY_URL = os.getenv("PROXY_URL")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
MAX_ERRORS_BEFORE_EMAIL = int(os.getenv("MAX_ERRORS_BEFORE_EMAIL", 5))

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Global error counter
error_count = 0

def validate_file_content(file_path: str) -> List[str]:
    """Validate that file exists and contains data."""
    try:
        if not os.path.exists(file_path):
            logging.error(f"File not found: {file_path}")
            return []
        with open(file_path, 'r') as file:
            content = file.readlines()
        return [line.strip() for line in content if line.strip()]
    except Exception as e:
        logging.error(f"Error reading {file_path}: {e}")
        return []

async def fetch_url(session: aiohttp.ClientSession, url: str) -> str:
    """Fetch the content of a URL asynchronously."""
    try:
        async with session.get(url, proxy=PROXY_URL) as response:
            if response.status != 200:
                logging.error(f"Failed to fetch URL {url} - Status Code: {response.status}")
                return ""
            return await response.text()
    except Exception as e:
        global error_count
        error_count += 1
        logging.error(f"Error fetching URL {url}: {e}")
        return ""

def get_authenticated_service():
    """Authenticate and return a YouTube API client."""
    try:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
        credentials = flow.run_console()
        return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
    except Exception as e:
        logging.error(f"Authentication failed: {e}")
        return None

async def scrape_video_links(session: aiohttp.ClientSession, keyword: str) -> List[str]:
    """Scrape video links from YouTube based on a keyword."""
    try:
        url = f'https://www.youtube.com/results?q={keyword}&sp=CAISAggBUBQ%253D'
        html_content = await fetch_url(session, url)
        if not html_content:
            return []
        soup = BeautifulSoup(html_content, 'html.parser')
        return [
            link.get('href').replace("/watch?v=", "")
            for link in soup.findAll('a', {'class': 'yt-uix-tile-link'})
            if link.get('href')
        ]
    except Exception as e:
        logging.error(f"Error scraping video links for keyword '{keyword}': {e}")
        return []

def comment_threads_insert(client, video_id: str, comment: str):
    """Post a comment on a YouTube video."""
    try:
        body = {
            'snippet': {
                'videoId': video_id,
                'topLevelComment': {
                    'snippet': {'textOriginal': comment}
                }
            }
        }
        response = client.commentThreads().insert(part='snippet', body=body).execute()
        logging.info(f"Comment posted on video {video_id}: {response}")
    except HttpError as e:
        global error_count
        error_count += 1
        logging.error(f"HTTP error occurred: {e}")
    except Exception as e:
        global error_count
        error_count += 1
        logging.error(f"An unexpected error occurred while posting a comment: {e}")

def send_email_notification():
    """Send an email notification if too many errors occur."""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER
        msg['Subject'] = "Error Notification: YouTube Bot"
        body = f"The bot encountered {error_count} errors. Please check the logs for details."
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
            logging.info("Error notification email sent.")
    except Exception as e:
        logging.error(f"Failed to send error notification email: {e}")

async def main():
    """Main function to execute the workflow."""
    global error_count

    client = get_authenticated_service()
    if not client:
        logging.error("Unable to initialize YouTube API client. Exiting.")
        return

    keywords = validate_file_content(KEYWORDS_FILE)
    comments = validate_file_content(COMMENTS_FILE)

    if not keywords or not comments:
        logging.error("Required data is missing. Exiting.")
        return

    async with aiohttp.ClientSession() as session:
        for keyword in keywords:
            video_links = await scrape_video_links(session, keyword)
            for video_id in video_links:
                if not video_id:
                    continue
                random_comment = random.choice(comments)
                comment_threads_insert(client, video_id, random_comment)

                if error_count >= MAX_ERRORS_BEFORE_EMAIL:
                    send_email_notification()
                    error_count = 0  # Reset error counter after notification

if __name__ == "__main__":
    asyncio.run(main())