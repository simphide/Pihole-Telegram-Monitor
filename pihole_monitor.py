import requests
import time
from datetime import datetime


class PiHole:
    """
    Saves a Pi-hole object with the following attributes:
    -IP-Address
    -Name
    -Users to inform
    -If Pi-hole is online
    -If the status is getting double checked
    """

    def __init__(self, ip: str, name: str, users: list):
        """
        Initialize Pi-hole object
        :param ip: ip-address of the pi-hole
        :param name: pretty name for the pi-hole
        :param users: users that should get notified
        """
        self.ip = ip
        self.online = True
        self.name = name
        self.users = users
        self.double_check = False


# Sleep time when starting script
INITIAL_SLEEP_TIME = 60
# Time to sleep between checks
REQUEST_INTERVAL = 60
# Timeout in seconds
REQUEST_TIMEOUT = 3

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


def telegram_bot_send_text(message: str, targets: list):
    """
    Send telegram message
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
                requests.get(send_text, timeout=REQUEST_TIMEOUT)
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


time.sleep(INITIAL_SLEEP_TIME)
while True:
    for device in PI_HOLES:
        answer = ""
        try:
            answer = requests.get("http://" + device.ip + "/admin/api.php", timeout=REQUEST_TIMEOUT)
        except requests.exceptions.RequestException:  # problem accessing the device
            if device.online:  # if it was online before
                if device.double_check:
                    device.online = False
                    device.double_check = False
                    telegram_bot_send_text(device.name + ": Device seems to be offline!", device.users)
                    continue
                else:
                    device.double_check = True
                    continue

        try:
            if answer.json()["status"] == "enabled" and not device.online:  # device is back online
                device.online = True
                telegram_bot_send_text(device.name + ": Device is online again!", device.users)
            elif answer.json()["status"] == "disabled" and device.online:  # adblocking is disabled
                if device.double_check:
                    device.online = False
                    telegram_bot_send_text(device.name + ": Ad-blocking function is disabled!", device.users)
                else:
                    device.double_check = True
                    continue
        except KeyError:
            if answer.json()["FTLnotrunning"] and device.online:  # FTL is not running
                if device.double_check:
                    device.online = False
                    telegram_bot_send_text(device.name + ": FTL is not running anymore!", device.users)
                else:
                    device.double_check = True
                    continue
            elif device.online:  # unknown error occurred
                if device.double_check:
                    device.online = False
                    telegram_bot_send_text(device.name + ": Unknown error occurred - " + answer.json(), device.users)
                else:
                    device.double_check = True
                    continue
        except AttributeError:  # sometimes triggered, when answer is empty
            pass

        # if the code reaches this line and the double check flag is set, we can unset is since nothing got triggered
        if device.double_check:
            device.double_check = False
            
    time.sleep(REQUEST_INTERVAL)
