import glob
import json
import os
import shutil
import time
from typing import Union

from discord_webhook import DiscordWebhook, DiscordEmbed

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
config_path = os.path.join(__location__, "config.json")

SIZE_STRINGS = ["KB", "MB", "GB", "TB", "PB"]


def calculate_usage(path: str) -> float:
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size


def bytes_to_string(num: Union[int, float]) -> float:
    """ Converts a byte value into a size string """
    i = 0
    ret = num / 1024
    while ret >= 1024 and i < 4:
        i += 1
        ret = ret / 1024
    return f"{ret:.2f}{SIZE_STRINGS[i]}"


def main():
    # Initialize the config variable
    config = None
    try:
        # Load the config from disk
        with open(config_path, "r") as fp:
            config = json.load(fp)
    except json.JSONDecodeError:
        quit("Error loading config from disk! Is it a valid JSON format?")
    try:
        print("Calculating usage percentages... this may take some time!")
        overall_usage_path = config.get("overall_usage_path", "/")
        paths_to_check = config.get("paths", [])
        webhook_url = config.get("webhook_url")
        if webhook_url is None:
            quit("PLEASE CONFIGURE A WEBHOOK URL FOR THE PROGRAM!")

        _total, _used, _free = shutil.disk_usage(overall_usage_path)
        free_percentage = round(_free / _total * 100, ndigits=2)

        # If the free space is below the configured threshold (or default 30%), start building a message
        ALERT = free_percentage <= config.get("alert_percentage", 30.0)

        # Do not touch :D (for testing purposes)
        _DEBUG = True

        if ALERT or _DEBUG:
            print("Disk usage threshold reached, posting an alert")

            # Build a Discord embed
            embed = DiscordEmbed(description=f"### Overall Usage\n**Total Space Used:** `{bytes_to_string(_used)}/{bytes_to_string(_total)}`\n", color="03b2f8")
            embed.set_author(name="Disk Usage Watchdog")

            # Add markdown-formatted text to the description
            markdown_text = "### Disk Usage By Path\n"
            for path in paths_to_check:
                path_usage = calculate_usage(path)
                usage_percentage = path_usage / _total * 100
                markdown_text += f"**File Path:** `{path}`\n**Usage:** `{usage_percentage:.2f}% ({bytes_to_string(path_usage)})`\n\n"

            embed.description += markdown_text

            # Add the free space info to the description
            embed.description += f"\nThere is currently {free_percentage}% of disk space available!"

            webhook = DiscordWebhook(url=webhook_url, username="Disk Usage Watchdog", content="")
            webhook.add_embed(embed)
            webhook.execute()
        else:
            print("Threshold for alert not met, not posting an alert")

    except KeyboardInterrupt:
        quit()


if __name__ == "__main__":
    main()
