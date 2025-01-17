
# YouTube Comment Bot (Modernized 2025)

This is a YouTube bot that posts comments on videos based on certain keywords. This version has been forked and updated with additional features such as proxy support, email notifications for errors, and asynchronous scraping.

## Features & Improvements:
- Asynchronous Web Scraping with aiohttp: Utilizes asynchronous requests to fetch YouTube pages more efficiently, reducing overall execution time.
- Proxy Support: Allows the use of proxy servers to avoid detection and IP blocking when performing web scraping. (optional for avoiding detection)
- Email Notifications for Error Thresholds: Sends an email notification when a defined number of errors occurs during execution, alerting the user to issues that need attention.
- Environment Variables via .env: Uses dotenv to load environment variables from a .env file, making it easier to configure settings such as API keys, proxy URLs, and email information without hardcoding them.
- Improved Error Handling: Implements a global error counter to track the number of errors, and if the threshold is exceeded, an email notification is sent.
- Data Validation: Ensures that important files such as keywords.txt and comments.txt exist and are not empty before the process continues.
- Better Code Structure with Functions and Logging: The code is now more modular, making it easier to understand, maintain, and extend. Logging has also been added to track important events, such as when comments are posted or errors occur.

## Requirements:
- Python 3+
- A YouTube Channel
- A YouTube API (You can follow the tutorial in the original video to get one)
- Proxy server URL (optional for avoiding detection)
- An email account to receive error notifications

## Modules:
- google-api-python-client
- google-auth-oauthlib
- google-auth-httplib2
- requests
- beautifulsoup4
- aiohttp
- python-dotenv
- smtplib

## Setup
1. Clone the repository:
   ```
   git clone https://github.com/LegendenSwe/Youtube-Comment-Bot.git
   cd Youtube-Comment-Bot
   ```

2. Create a `.env` file in the root directory of the project and add the following variables:
   ```
   CLIENT_SECRETS_FILE=path/to/your/client_secret.json
   EMAIL_SENDER=your-email@example.com
   EMAIL_RECEIVER=receiver-email@example.com
   EMAIL_PASSWORD=your-email-password
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   PROXY_URL=http://proxy-server:port
   MAX_ERRORS_BEFORE_EMAIL=5
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the bot:
   ```
   python yt.py
   ```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer
For educational purposes only.