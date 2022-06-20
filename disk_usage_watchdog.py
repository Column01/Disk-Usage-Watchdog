import glob
import json
import os
import shutil
import time
from typing import Union

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
config_path = os.path.join(__location__, "config.json")


def calculate_usage(path: str) -> float:
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size


def bytes_to_gigabytes(num: Union[int, float]) -> float:
    """ Converts a byte number into a GB total """
    return ((num / 1024) / 1024) / 1024


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
        _total, _used, _free = shutil.disk_usage(overall_usage_path)
        free_percentage = round(_free / _total * 100, ndigits=2)

        # If the free space is below the configured threshold (or default 30%), start building a message
        ALERT = free_percentage <= config.get("alert_percentage", 30.0)

        if ALERT:
            # Build a message for discord
            message = []
            message.append("```")
            message.append("DISK USAGE ALERT:")
            message.append(f"Used: {bytes_to_gigabytes(_used):.2f}GB/{bytes_to_gigabytes(_total):.2f}GB")
            message.append(f"There is currently {free_percentage}% of disk space available.")
            message.append("-" * 25)
            message.append("Disk usage by path:")
            message.append("-" * 25)
            message.append("Path    % usage    Size (GB)")

            # Check all paths and their usages
            for path in paths_to_check:
                path_usage = calculate_usage(path)
                usage_percentage = round(path_usage / _total * 100, ndigits=2)
                formatted_usage = f"{path}    {usage_percentage}%    {bytes_to_gigabytes(path_usage):4f}GB"
                message.append(formatted_usage)

            message.append("```")
            print("\n".join(message))

    except KeyboardInterrupt:
        quit()


if __name__ == "__main__":
    main()
