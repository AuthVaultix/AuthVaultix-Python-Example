import os
import json
import time
import requests
import platform
import binascii

class api:
    def __init__(self, name, ownerid, secret, version, api_url):

        if not ownerid or len(ownerid) < 10:
            raise ValueError("Invalid ownerid")
        if not secret or len(secret) < 64:
            raise ValueError("Invalid secret")
        if not api_url.startswith("http"):
            raise ValueError("Invalid API URL (must start with http/https)")

        self.name = name
        self.ownerid = ownerid
        self.secret = secret
        self.version = version
        self.api_url = api_url
        self.sessionid = ""
        self.initialized = False
        self.user_data = {}
        self.app_data = {}

        self.init()

    def init(self):
        if self.sessionid:
            print("Already initialized!")
            return

        enckey = binascii.hexlify(os.urandom(16)).decode()
        post_data = {
            "type": "init",
            "name": self.name,
            "ownerid": self.ownerid,
            "ver": self.version,
            "enckey": enckey
        }

        response = self.__do_request(post_data)
        if response == "Authvaultix_Invalid":
            print("Invalid application or ownerid")
            return

        data = json.loads(response)
        if not data.get("success"):
            print("Init failed:", data.get("message"))
            return

        self.sessionid = data["sessionid"]
        self.app_data = data["appinfo"]
        self.initialized = True
        print("Initialization successful!")

    def login(self, username, password):
        self._check_init()
        post_data = {
            "type": "login",
            "username": username,
            "pass": password,
            "sessionid": self.sessionid,
            "name": self.name,
            "ownerid": self.ownerid
        }

        response = self.__do_request(post_data)
        data = json.loads(response)

        if data.get("success"):
            self.user_data = data["info"]
            print("Login successful!")
            return True   # ✅ ADD
        else:
            print("Login failed:", data.get("message"))
            return False  # ✅ ADD

    def register(self, username, password, license_key, hwid=None):
        self._check_init()
        if not hwid:
            hwid = self.get_hwid()

        post_data = {
            "type": "register",
            "username": username,
            "pass": password,
            "key": license_key,
            "hwid": hwid,
            "sessionid": self.sessionid,
            "name": self.name,
            "ownerid": self.ownerid
        }

        response = self.__do_request(post_data)
        data = json.loads(response)
        if data.get("success"):
            self.user_data = data["info"]
            print("Registration successful!")
        else:
            print("Registration failed:", data.get("message"))

    def license(self, license_key, hwid=None):
        self._check_init()
        if not hwid:
            hwid = self.get_hwid()

        post_data = {
            "type": "license",
            "key": license_key,
            "sessionid": self.sessionid,
            "name": self.name,
            "ownerid": self.ownerid,
            "hwid": hwid
        }

        response = self.__do_request(post_data)
        data = json.loads(response)
        if data.get("success"):
            self.user_data = data["info"]
            print("License applied successfully!")
        else:
            print("License failed:", data.get("message"))

    def var(self, var_name):
        self._check_init()
        post_data = {
            "type": "var",
            "varid": var_name,
            "sessionid": self.sessionid,
            "name": self.name,
            "ownerid": self.ownerid
        }
        response = self.__do_request(post_data)
        data = json.loads(response)
        if data.get("success"):
            return data.get("message")
        else:
            print("Failed to fetch variable:", data.get("message"))
            return None

    def setvar(self, var_name, var_data):
        self._check_init()
        post_data = {
            "type": "setvar",
            "var": var_name,
            "data": var_data,
            "sessionid": self.sessionid,
            "name": self.name,
            "ownerid": self.ownerid
        }
        response = self.__do_request(post_data)
        data = json.loads(response)
        if data.get("success"):
            return True
        else:
            print("Failed to set variable:", data.get("message"))
            return False

    def logout(self):
        self._check_init()
        post_data = {
            "type": "logout",
            "sessionid": self.sessionid,
            "name": self.name,
            "ownerid": self.ownerid
        }
        response = self.__do_request(post_data)
        data = json.loads(response)
        if data.get("success"):
            print("Logged out successfully!")
            self.sessionid = ""
            self.initialized = False
        else:
            print("Logout failed:", data.get("message"))

    # =================== INTERNAL METHODS ===================
    def __do_request(self, post_data):
        try:
            response = requests.post(self.api_url, data=post_data, timeout=10)
            return response.text
        except requests.exceptions.Timeout:
            print("Request timed out. Server may be down/slow.")
            return "{}"

    def _check_init(self):
        if not self.initialized:
            raise Exception("Client not initialized. Call init() first.")

    @staticmethod
    def get_hwid():
        system = platform.system()
        try:
            if system == "Windows":
                import win32security
                user = os.getlogin()
                sid = win32security.LookupAccountName(None, user)[0]
                return win32security.ConvertSidToStringSid(sid)
            elif system == "Linux":
                with open("/etc/machine-id") as f:
                    return f.read().strip()
            elif system == "Darwin":
                import subprocess
                output = subprocess.check_output("ioreg -l | grep IOPlatformSerialNumber", shell=True)
                serial = output.decode().split('=')[1].replace(' ', '').strip('"')
                return serial
        except Exception:
            return "UNKNOWN_HWID"
