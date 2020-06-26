import requests
import time
from datetime import datetime


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


class PiHole:
    """
    Saves a Pi-hole object with the following attributes:
    -IP-Address
    -Name
    -Users to inform
    -If Pi-hole is online
    -If the status is getting double checked
    """

    def __init__(self, ip: str, name: str, users: list, max_retries: int = 1, request_timeout: int = 3,
                 retry_time: int = 15):
        """
        Initialize Pi-hole object
        :param ip: IP of the Pi-hole
        :param name: Pretty name of the Pi-hole
        :param users: Users to inform
        :param max_retries: number of retries before a status code is returned
        :param request_timeout: time until a request times out
        :param retry_time: time to wait between approaches to access the Pi-hole
        """
        self.ip = ip
        self.online = True
        self.name = name
        self.users = users
        self.retry_number = 0
        self.max_retries = max_retries
        self.request_timeout = request_timeout
        self.retry_time = retry_time

    def get_status(self) -> int:
        """
        Returns status code as an integer
        0 - status hasn't changed
        1 - Pi-hole is alive
        2 - Pi-hole is down
        3 - Ad-blocking function is deactivated
        4 - FTL is not running anymore
        5 - unknown error occurred
        :return: integer between 0-5
        """
        r = ""
        try:
            r = requests.get("http://" + device.ip + "/admin/api.php", timeout=self.request_timeout)
        except requests.exceptions.RequestException:  # problem accessing the device
            if self.online:  # if it was online before
                if self.retry_number >= self.max_retries:
                    self.online = False
                    self.retry_number = 0
                    return 2
                else:
                    self.retry_number += 1
                    time.sleep(self.retry_time)
                    return self.get_status()

        try:
            if r.json()["status"] == "enabled" and not self.online:  # device is back online
                self.online = True
                self.retry_number = 0
                return 1
            elif r.json()["status"] == "disabled" and self.online:  # ad-blocking is disabled
                if self.retry_number >= self.max_retries:
                    self.online = False
                    self.retry_number = 0
                    return 3
                else:
                    self.retry_number += 1
                    time.sleep(self.retry_time)
                    return self.get_status()
        except KeyError:
            if r.json()["FTLnotrunning"] and self.online:  # FTL is not running
                if self.retry_number >= self.max_retries:
                    self.online = False
                    self.retry_number = 0
                    return 4
                else:
                    self.retry_number += 1
                    time.sleep(self.retry_time)
                    return self.get_status()
            elif self.online:  # unknown error occurred
                if self.retry_number >= self.max_retries:
                    self.online = False
                    self.retry_number = 0
                    return 5
                else:
                    self.retry_number += 1
                    time.sleep(self.retry_time)
                    return self.get_status()
        except AttributeError:  # sometimes triggered, when answer is empty
            pass
        return 0


# Sleep time when starting script
INITIAL_SLEEP_TIME = 60
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
