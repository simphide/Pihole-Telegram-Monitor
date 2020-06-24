import requests
import time
from datetime import datetime

# Sleep time when starting script
INITIAL_SLEEP_TIME = 30
# Time to sleep between checks
SLEEP_TIME = 10
# Timeout in seconds
REQUESTS_TIMEOUT = 3

# Telegram Bot API-Key
TELEGRAM_API_KEY = ""
# Chat-IDs of the users that will be informed
TELEGRAM_CHAT_IDS = [
    "XXXXX"
]

# List of Pi-holes to check
PI_HOLE_ADDRESSES = {
    "XXX.XXX.XXX.XXX": True,
}


def telegram_bot_send_text(message):
    """
    Send telegram message
    :param message: message to send all chats
    :return: nothing
    """
    print_message(message)
    for chat_id in TELEGRAM_CHAT_IDS:
        send_text = 'https://api.telegram.org/bot' + TELEGRAM_API_KEY \
                    + '/sendMessage?chat_id=' + chat_id \
                    + '&text=' + message
        try:
            requests.get(send_text, timeout=REQUESTS_TIMEOUT)
        except requests.exceptions.RequestException as e:
            print_message("Exception raised while sending telegram message: " + str(e))


def print_message(message):
    """
    Prints message including time and date
    :param message: message to be printed
    :return: nothing
    """
    print("[" + datetime.today().strftime("%Y-%m-%d") + " - " + str(time.strftime("%H:%M:%S")) + "] "
          + message)


time.sleep(INITIAL_SLEEP_TIME)
while True:
    for device in PI_HOLE_ADDRESSES:
        answer = ""
        try:
            answer = requests.get("http://" + device + "/admin/api.php", timeout=REQUESTS_TIMEOUT)
        except requests.exceptions.RequestException:
            if PI_HOLE_ADDRESSES[device]:
                telegram_bot_send_text(device + " - Pi-hole seems to be offline!")
                PI_HOLE_ADDRESSES[device] = False
                continue

        try:
            if answer.json()["status"] == "enabled" and not PI_HOLE_ADDRESSES[device]:
                telegram_bot_send_text(device + " - Pi-hole is back online again!")
                PI_HOLE_ADDRESSES[device] = True
            elif answer.json()["status"] == "disabled" and PI_HOLE_ADDRESSES[device]:
                telegram_bot_send_text(device + " - Pi-holes ad-blocking function is disabled!")
                PI_HOLE_ADDRESSES[device] = False
        except KeyError:
            if answer.json()["FTLnotrunning"] and PI_HOLE_ADDRESSES[device]:
                telegram_bot_send_text(device + " - FTL is not running anymore!")
                PI_HOLE_ADDRESSES[device] = False
            elif PI_HOLE_ADDRESSES[device]:
                telegram_bot_send_text(device + " - Unknown error occurred: " + answer.json())
                PI_HOLE_ADDRESSES[device] = False
        except AttributeError:
            pass
    time.sleep(SLEEP_TIME)
