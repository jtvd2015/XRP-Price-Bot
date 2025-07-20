\# XRP Price Bot



A Python bot that sends twice-daily XRP portfolio updates, market stats, news headlines, sentiment analysis, and a random fun fact to your email.



\## Features



\- Tracks your XRP portfolio value (private per recipient)

\- Sends updates at 6am and 6pm daily

\- Includes a 24-hour price chart image

\- Fetches latest XRP news headlines

\- Analyzes news sentiment (positive/neutral/negative)

\- Adds a random crypto tip or fun fact



\## Setup



1\. \*\*Clone this repo.\*\*

2\. \*\*Create a `.env` file\*\* in the project root with your email and API credentials:

&nbsp;   ```

&nbsp;   EMAIL\_USER=your\_email@example.com

&nbsp;   EMAIL\_PASS=your\_email\_password

&nbsp;   CRYPTOPANIC\_API\_KEY=your\_cryptopanic\_api\_key



&nbsp;   PORTFOLIO1\_NAME=YourName

&nbsp;   PORTFOLIO1\_AMOUNT=XXX

&nbsp;   PORTFOLIO1\_EMAIL=your\_email@example.com



&nbsp;   PORTFOLIO2\_NAME=Friend

&nbsp;   PORTFOLIO2\_AMOUNT=XXX

&nbsp;   PORTFOLIO2\_EMAIL=friend@example.com

&nbsp;   ```

3\. \*\*Install dependencies:\*\*

&nbsp;   ```

&nbsp;   pip install -r requirements.txt

&nbsp;   ```

4\. \*\*Edit your `.env` to add/remove portfolio users as needed.\*\*

5\. \*\*Schedule the script to run at 6am and 6pm (see below).\*\*



\## Scheduling



\- \*\*Windows:\*\* Use Task Scheduler to run the script at 6am and 6pm.

\- \*\*Linux:\*\* Add to your crontab:

&nbsp;   ```

&nbsp;   0 6,18 \* \* \* /usr/bin/python3 /path/to/xrp\_telegram\_bot.py

&nbsp;   ```



\## Security



\*\*Never commit your `.env` file or any secrets to GitHub!\*\*  

This project is set up to keep your credentials private.



\## License



MIT

