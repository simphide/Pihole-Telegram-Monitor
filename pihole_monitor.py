import requests
import time

# Time to sleep between checks
SLEEP_TIME = 10


# Telegram Bot API-Key
TELEGRAM_API_KEY = ""

# Chat-IDs of the users that will be informed
TELEGRAM_CHAT_IDS = [
    "XXXXXXXX"
]


# List of Pi-holes to check
PI_HOLE_ADDRESSES = {
    "192.168.178.XXXX": True
}


def telegram_bot_send_text(bot_message):
    """
    Send telegram message
    :param bot_message: message to send all chats
    :return: nothing
    """
    print(bot_message)
    for chat_id in TELEGRAM_CHAT_IDS:
        send_text = 'https://api.telegram.org/bot' + TELEGRAM_API_KEY \
                    + '/sendMessage?chat_id=' + chat_id \
                    + '&text=' + bot_message
        requests.get(send_text)


while True:
    for device in PI_HOLE_ADDRESSES:
        answer = ""
        try:
            answer = requests.get("http://" + device + "/admin/api.php")
        except requests.exceptions.RequestException:
            if PI_HOLE_ADDRESSES[device]:
                telegram_bot_send_text("[" + device + "] Pi-hole seems to be offline!")
                PI_HOLE_ADDRESSES[device] = False
                continue

        try:
            if answer.json()["status"] == "enabled" and not PI_HOLE_ADDRESSES[device]:
                telegram_bot_send_text("[" + device + "] Pi-hole is back online again!")
                PI_HOLE_ADDRESSES[device] = True
            elif answer.json()["status"] == "disabled" and PI_HOLE_ADDRESSES[device]:
                telegram_bot_send_text("[" + device + "] Pi-holes ad-blocking function is disabled!")
                PI_HOLE_ADDRESSES[device] = False
        except KeyError:
            if answer.json()["FTLnotrunning"] and PI_HOLE_ADDRESSES[device]:
                telegram_bot_send_text("[" + device + "] FTL is not running anymore!")
                PI_HOLE_ADDRESSES[device] = False
            elif PI_HOLE_ADDRESSES[device]:
                telegram_bot_send_text("[" + device + "] Unknown error occurred: " + answer.json())
                PI_HOLE_ADDRESSES[device] = False
        except AttributeError:
            pass
    time.sleep(SLEEP_TIME)
