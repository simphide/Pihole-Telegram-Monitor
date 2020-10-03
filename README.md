# Pihole-Telegram-Monitor

Monitor list of Pi-holes and notify specific persons via Telegram if a Pi-hole is down.

## Author

* [Simphide](https://github.com/simphide)

## Requirements

* requests
* datetime 

Both modules can be installed via  `requirements.txt`

## Config

```python
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
```



