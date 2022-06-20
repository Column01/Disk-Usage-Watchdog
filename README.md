# Disk-Usage-Watchdog

A python script designed to send an alert to a discord webhook if your disk usage gets too high

# Installation

1. Clone the repository
    - `git clone https://github.com/Column01/Disk-Usage-Watchdog.git`
2. Install Python 3.6 or newer (get the latest)
3. Install the `discord-webhook` library:
    - Unix: `pip install discord-webhook`
    - Windows: `python -m pip install discord-webhook`
4. Configure the program
    - Open `config.json` in a text editor
    - Set the path to the root of your file system to calculate overall disk usage (`C://` on Windows, `/` on Unix)
    - Set the threshold of **FREE** space left before you want for alerts (as a float percentage. So if you wanted 25% free, put 25.0)
    - Set the webhook URL to the webhook URL for your channel on discord
    - Add any paths you want to explicitly check if your free disk space is below the threshold you set in your config. If you just want general alerts, just leave it empty.
5. Setup some way to run the script periodically. On Windows I believe you can use the task scheduler, and on Unix you can use Cron
    - Unix Command: `python3 disk_usage_watchdog.py`
    - Windows Command: `python disk_usage_watchdog.py`
