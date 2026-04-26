import os
import json
import time
import requests
import platform
import binascii
import subprocess
import hashlib


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

        response = self.do_request(post_data)
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

    def login(self, username, password, hwid=None):
        self._check_init()

        if not hwid:
            hwid = self.get_hwid()   

        post_data = {
            "type": "login",
            "username": username,
            "pass": password,
            "hwid": hwid,  
            "sessionid": self.sessionid,
            "name": self.name,
            "ownerid": self.ownerid
        }

        response = self.do_request(post_data)
        data = json.loads(response)

        if data.get("success"):
            self.user_data = data["info"]
            print("Login successful!")
            return True
        else:
            print("Login failed:", data.get("message"))
            return False

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

        response = self.do_request(post_data)
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

        response = self.do_request(post_data)
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
        response = self.do_request(post_data)
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
        response = self.do_request(post_data)
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
        response = self.do_request(post_data)
        data = json.loads(response)
        if data.get("success"):
            print("Logged out successfully!")
            self.sessionid = ""
            self.initialized = False
        else:
            print("Logout failed:", data.get("message"))

    # =================== INTERNAL METHODS ===================
    def do_request(self, post_data):
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
    def hwid_to_sid(hwid):
        try:
            parts = [
                hwid[0:8],
                hwid[8:16],
                hwid[16:24],
                hwid[24:32]
            ]
            nums = [str(int(p, 16)) for p in parts]
            return f"S-1-5-21-{nums[0]}-{nums[1]}-{nums[2]}-{nums[3]}"
        except:
            return "INVALID_SID"

    @staticmethod
    def get_hwid():
        system = platform.system()
        try:
            data = ""

            if system == "Windows":
                cpu = subprocess.check_output("wmic cpu get ProcessorId", shell=True).decode().split("\n")[1].strip()
                disk = subprocess.check_output("wmic diskdrive get SerialNumber", shell=True).decode().split("\n")[1].strip()
                board = subprocess.check_output("wmic baseboard get SerialNumber", shell=True).decode().split("\n")[1].strip()
                guid = subprocess.check_output(
                    'reg query HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Cryptography /v MachineGuid',
                    shell=True
                ).decode().split()[-1]

                data = cpu + disk + board + guid

            elif system == "Linux":
                with open("/etc/machine-id") as f:
                    machine = f.read().strip()

                cpu = subprocess.getoutput("cat /proc/cpuinfo | grep Serial | awk '{print $3}'")
                disk = subprocess.getoutput("lsblk -o SERIAL | head -n 2 | tail -n 1")

                data = machine + cpu + disk

            elif system == "Darwin":
                serial = subprocess.check_output(
                    "system_profiler SPHardwareDataType | grep 'Serial Number'",
                    shell=True
                ).decode().split(":")[1].strip()

                data = serial

            # 🔒 Step 1: Hash
            hwid_hash = hashlib.sha256(data.encode()).hexdigest()

            # 🔒 Step 2: Convert to SID format
            return api.hwid_to_sid(hwid_hash)

        except Exception:
            return "UNKNOWN_HWID"
