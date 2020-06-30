import requests
import time


class PiHole:
    """
    A Pi-hole object containing the IP-address, pretty name and other relevant information.
    """

    def __init__(self, ip: str, name: str, users: list, max_retries: int = 1, request_timeout: int = 3,
                 retry_time: int = 15, connection_check_server: str = "https://1.1.1.1/",
                 connection_secure: bool = True):
        """
        Initialize Pi-hole object
        :param ip: IP of the Pi-hole
        :param name: Pretty name of the Pi-hole
        :param users: Users belonging to the Pi-hole
        :param max_retries: number of retries before a status code is returned
        :param request_timeout: time until a request times out
        :param retry_time: time to wait between approaches to access the Pi-hole
        :param connection_check_server: server to check if internet is available
        :param connection_secure: is the ssl certificate valid?
        """
        self.ip = ip
        self.online = True
        self.name = name
        self.users = users
        self.retry_number = 0
        self.max_retries = max_retries
        self.request_timeout = request_timeout
        self.retry_time = retry_time
        self.connection_check_server = connection_check_server
        self.connection_secure = connection_secure
        if not connection_secure:
            requests.packages.urllib3.disable_warnings()

    def get_status(self) -> int:
        """
        Returns status code as an integer
        -1 - no internet connection available
        0  - status hasn't changed
        1  - Pi-hole is alive
        2  - Pi-hole is down
        3  - Ad-blocking function is deactivated
        4  - FTL is not running anymore
        5  - unknown error occurred
        :return: integer between 0-5; -1 when no internet is available
        """
        try:  # test if internet is available
            requests.get(self.connection_check_server, timeout=self.request_timeout, verify=self.connection_secure)
        except requests.exceptions.RequestException:
            self.retry_number = 0
            return -1

        r = ""
        try:
            r = requests.get("http://" + self.ip + "/admin/api.php", timeout=self.request_timeout)
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
