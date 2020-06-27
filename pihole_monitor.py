import time
from datetime import datetime
import requests
from pihole import PiHole


def telegram_bot_send_text(message: str, targets: list, request_timeout: int = 3):
    """
    Send telegram message
    :param request_timeout: time until requests times out
    :param targets: list of persons that should receive the message
    :param message: message to send all chats
    :return: nothing
    """
    print_message(message)
    for chat_id in TELEGRAM_CHAT_IDS:
        if chat_id in targets:
            send_text = "https://api.telegram.org/bot" + TELEGRAM_API_KEY \
                        + "/sendMessage?chat_id=" + TELEGRAM_CHAT_IDS[chat_id] \
                        + "&text=" + message
            try:
                requests.get(send_text, timeout=request_timeout)
            except requests.exceptions.RequestException as e:
                print_message("Exception raised while sending telegram message: " + str(e))


def print_message(message: str):
    """
    Prints message including time and date
    :param message: message to be printed
    :return: nothing
    """
    print("[" + datetime.today().strftime("%Y-%m-%d") + " - " + str(time.strftime("%H:%M:%S")) + "] "
          + message)


# Sleep time when starting script
INITIAL_SLEEP_TIME = 0
# Time to sleep between checks
REQUEST_INTERVAL = 60

# Telegram Bot API-Key
TELEGRAM_API_KEY = "XXXXXXXX"
# Chat-IDs of the users that will be informed
TELEGRAM_CHAT_IDS = {
    "Peter": "12345",
}

# List of Pi-holes to check
PI_HOLES = [
    PiHole("XXX.XXX.XXX.XXX", "Peters Pi-hole", ["Peter"])
]

time.sleep(INITIAL_SLEEP_TIME)
while True:
    for device in PI_HOLES:
        status_code = device.get_status()
        if status_code == 1:
            telegram_bot_send_text(device.name + ": Device is online again!", device.users)
        elif status_code == 2:
            telegram_bot_send_text(device.name + ": Device seems to be offline!", device.users)
        elif status_code == 3:
            telegram_bot_send_text(device.name + ": Ad-blocking function is disabled!", device.users)
        elif status_code == 4:
            telegram_bot_send_text(device.name + ": FTL is not running anymore!", device.users)
        elif status_code == 5:
            telegram_bot_send_text(device.name + ": Unknown error occurred...", device.users)
    time.sleep(REQUEST_INTERVAL)

