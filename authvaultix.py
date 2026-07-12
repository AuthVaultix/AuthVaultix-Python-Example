import os
import json
import requests
import platform
import binascii
import subprocess
import hashlib
from datetime import datetime

class AuthVaultixClient:
    def __init__(self, app_name, owner_id, secret, version, api_url="https://authvaultix.com/api/1.0/"):
        self._core = AuthVaultixCore(app_name, owner_id, secret, version, api_url)
        self.init()

    @property
    def current_user(self):
        return self._core.current_user

    @property
    def session_id(self):
        return self._core.session_id

    @property
    def initialized(self):
        return self._core.initialized

    def init(self):
        return self._core.initialize_context()

    def login(self, username, password):
        return self._core.authenticate_user(username, password)

    def register(self, username, password, license_key, email=""):
        return self._core.register_account(username, password, license_key, email)

    def license_login(self, license_key):
        return self._core.license_access(license_key)

    def logout(self):
        self._core.terminate_session()

    def get_var(self, var_name):
        return self._core.fetch_user_variable(var_name)

    def get_global_var(self, var_key):
        return self._core.fetch_global_variable(var_key)

    def set_var(self, var_name, value):
        return self._core.update_user_variable(var_name, value)

    def check(self):
        return self._core.validate_session()

    def log(self, message):
        return self._core.send_log(message)

    def download(self, file_id):
        return self._core.retrieve_file(file_id)

    def fetch_online(self):
        return self._core.get_online_clients()

    def ban(self, reason=""):
        return self._core.enforce_ban(reason)

    def change_username(self, new_username):
        return self._core.update_username(new_username)

    def check_blacklist(self):
        return self._core.verify_blacklist()

    def forgot_password(self, username, email):
        return self._core.trigger_password_reset(username, email)

    def upgrade(self, username, license_key):
        return self._core.apply_upgrade(username, license_key)

    def chat_send(self, message, channel):
        return self._core.transmit_chat_message(message, channel)

    def chat_fetch(self, channel):
        return self._core.retrieve_chat_history(channel)

    def webhook(self, web_id, param, body="", conttype=""):
        return self._core.trigger_webhook(web_id, param, body, conttype)

    def fetch_stats(self):
        return self._core.fetch_statistics()

    def get_user_info(self):
        return self._core.get_formatted_user_info()


class AuthVaultixCore:
    def __init__(self, app_name, owner_id, secret, version, api_url):
        self._app_name = app_name
        self._owner_id = owner_id
        self._secret = secret
        self._version = version
        self._api_url = api_url

        self.session_id = ""
        self.initialized = False
        self.current_user = {}
        self.app_info = {}

    def _ensure_ready(self):
        if not self.initialized:
            raise Exception("SDK not initialized. Call client.init() before using any API.")

    def initialize_context(self):
        if self.initialized:
            return True

        encryption_key = binascii.hexlify(os.urandom(16)).decode()

        payload = PayloadBuilder("init") \
            .with_value("ver", self._version) \
            .with_value("enckey", encryption_key) \
            .with_value("name", self._app_name) \
            .with_value("ownerid", self._owner_id) \
            .compile()

        resp = NetworkAgent.post(self._api_url, payload)

        if resp == "Authvaultix_Invalid":
            print("Application not found.")
            return False

        try:
            dto = json.loads(resp)
        except Exception:
            print("Invalid JSON response")
            return False

        if not dto.get("success"):
            print("Initialization failed:", dto.get("message"))
            return False

        self.session_id = dto.get("sessionid")
        self.app_info = dto.get("appinfo", {})
        self.initialized = True
        print("Initialization successful!")
        return True

    def authenticate_user(self, username, password):
        self._ensure_ready()
        
        payload = PayloadBuilder("login") \
            .with_context(self._app_name, self._owner_id, self.session_id) \
            .with_value("username", username) \
            .with_value("pass", password) \
            .with_value("hwid", HardwareIdentifier.fetch()) \
            .with_value("version", self._version) \
            .with_value("os", SystemInfoCollector.get_os_version()) \
            .with_value("platform", SystemInfoCollector.get_platform()) \
            .with_value("device", SystemInfoCollector.get_device_type()) \
            .with_value("architecture", SystemInfoCollector.get_architecture()) \
            .with_value("cpu_cores", SystemInfoCollector.get_cpu_cores()) \
            .with_value("ram", SystemInfoCollector.get_ram_gb()) \
            .compile()

        resp = NetworkAgent.post(self._api_url, payload)
        
        try:
            dto = json.loads(resp)
        except Exception:
            print("Login failed: Invalid Server Response")
            return False

        if not dto.get("success"):
            print("Login failed:", dto.get("message"))
            return False

        self.current_user = dto.get("info", {})
        if dto.get("sessionid"):
            self.session_id = dto.get("sessionid")
        print("Login successful!")
        return True

    def register_account(self, username, password, license_key, email):
        self._ensure_ready()
        
        payload = PayloadBuilder("register") \
            .with_context(self._app_name, self._owner_id, self.session_id) \
            .with_value("username", username) \
            .with_value("pass", password) \
            .with_value("key", license_key) \
            .with_value("email", email) \
            .with_value("hwid", HardwareIdentifier.fetch()) \
            .with_value("version", self._version) \
            .with_value("os", SystemInfoCollector.get_os_version()) \
            .with_value("platform", SystemInfoCollector.get_platform()) \
            .with_value("device", SystemInfoCollector.get_device_type()) \
            .with_value("architecture", SystemInfoCollector.get_architecture()) \
            .with_value("cpu_cores", SystemInfoCollector.get_cpu_cores()) \
            .with_value("ram", SystemInfoCollector.get_ram_gb()) \
            .compile()

        resp = NetworkAgent.post(self._api_url, payload)
        try:
            dto = json.loads(resp)
        except Exception:
            print("Registration failed: Invalid Server Response")
            return False

        if not dto.get("success"):
            print("Registration failed:", dto.get("message"))
            return False

        self.current_user = dto.get("info", {})
        if dto.get("sessionid"):
            self.session_id = dto.get("sessionid")
        print("Registration successful!")
        return True

    def license_access(self, license_key):
        self._ensure_ready()
        
        payload = PayloadBuilder("license") \
            .with_context(self._app_name, self._owner_id, self.session_id) \
            .with_value("key", license_key) \
            .with_value("hwid", HardwareIdentifier.fetch()) \
            .with_value("version", self._version) \
            .with_value("os", SystemInfoCollector.get_os_version()) \
            .with_value("platform", SystemInfoCollector.get_platform()) \
            .with_value("device", SystemInfoCollector.get_device_type()) \
            .with_value("architecture", SystemInfoCollector.get_architecture()) \
            .with_value("cpu_cores", SystemInfoCollector.get_cpu_cores()) \
            .with_value("ram", SystemInfoCollector.get_ram_gb()) \
            .compile()

        resp = NetworkAgent.post(self._api_url, payload)
        try:
            dto = json.loads(resp)
        except Exception:
            print("License application failed: Invalid Server Response")
            return False

        if not dto.get("success"):
            print("License failed:", dto.get("message"))
            return False

        self.current_user = dto.get("info", {})
        if dto.get("sessionid"):
            self.session_id = dto.get("sessionid")
        print("License applied successfully!")
        return True

    def fetch_global_variable(self, var_key):
        self._ensure_ready()
        payload = PayloadBuilder("var") \
            .with_context(self._app_name, self._owner_id, self.session_id) \
            .with_value("varid", var_key) \
            .compile()

        resp = NetworkAgent.post(self._api_url, payload)
        try:
            dto = json.loads(resp)
        except Exception:
            return None

        if not dto.get("success"):
            print("Failed to fetch global variable:", dto.get("message"))
            return None

        return dto.get("message")

    def fetch_user_variable(self, var_name):
        self._ensure_ready()
        payload = PayloadBuilder("getvar") \
            .with_context(self._app_name, self._owner_id, self.session_id) \
            .with_value("var", var_name) \
            .compile()

        resp = NetworkAgent.post(self._api_url, payload)
        try:
            dto = json.loads(resp)
        except Exception:
            return None

        if not dto.get("success"):
            print("Failed to fetch user variable:", dto.get("message"))
            return None

        return dto.get("response")

    def update_user_variable(self, var_name, value):
        self._ensure_ready()
        payload = PayloadBuilder("setvar") \
            .with_context(self._app_name, self._owner_id, self.session_id) \
            .with_value("var", var_name) \
            .with_value("data", value) \
            .compile()

        resp = NetworkAgent.post(self._api_url, payload)
        try:
            dto = json.loads(resp)
        except Exception:
            return False

        if not dto.get("success"):
            print("Failed to set variable:", dto.get("message"))
            return False

        return True

    def validate_session(self):
        self._ensure_ready()
        payload = PayloadBuilder("check") \
            .with_context(self._app_name, self._owner_id, self.session_id) \
            .compile()
        resp = NetworkAgent.post(self._api_url, payload)
        try:
            dto = json.loads(resp)
            return dto.get("success", False)
        except Exception:
            return False

    def send_log(self, message):
        self._ensure_ready()
        payload = PayloadBuilder("log") \
            .with_context(self._app_name, self._owner_id, self.session_id) \
            .with_value("message", message) \
            .with_value("pcuser", os.getenv('USERNAME') or os.getenv('USER') or "Unknown") \
            .compile()
        resp = NetworkAgent.post(self._api_url, payload)
        try:
            dto = json.loads(resp)
            if not dto.get("success"):
                print("Log failed:", dto.get("message"))
                return False
            return True
        except Exception:
            return False

    def retrieve_file(self, file_id):
        self._ensure_ready()
        payload = PayloadBuilder("file") \
            .with_context(self._app_name, self._owner_id, self.session_id) \
            .with_value("fileid", file_id) \
            .compile()
        resp = NetworkAgent.post(self._api_url, payload)
        try:
            dto = json.loads(resp)
            if not dto.get("success"):
                print("Download failed:", dto.get("message"))
                return None
            return binascii.unhexlify(dto.get("contents"))
        except Exception:
            return None

    def get_online_clients(self):
        self._ensure_ready()
        payload = PayloadBuilder("fetchOnline") \
            .with_context(self._app_name, self._owner_id, self.session_id) \
            .compile()
        resp = NetworkAgent.post(self._api_url, payload)
        try:
            dto = json.loads(resp)
            if not dto.get("success"):
                return None
            return dto.get("users", [])
        except Exception:
            return None

    def enforce_ban(self, reason):
        self._ensure_ready()
        payload = PayloadBuilder("ban") \
            .with_context(self._app_name, self._owner_id, self.session_id) \
            .with_value("reason", reason) \
            .compile()
        resp = NetworkAgent.post(self._api_url, payload)
        try:
            dto = json.loads(resp)
            if not dto.get("success"):
                print("Ban failed:", dto.get("message"))
                return False
            return True
        except Exception:
            return False

    def update_username(self, new_username):
        self._ensure_ready()
        payload = PayloadBuilder("changeUsername") \
            .with_context(self._app_name, self._owner_id, self.session_id) \
            .with_value("newUsername", new_username) \
            .compile()
        resp = NetworkAgent.post(self._api_url, payload)
        try:
            dto = json.loads(resp)
            if dto.get("success"):
                print("Username changed successfully. Logging out...")
                self.session_id = ""
                self.initialized = False
                return True
            else:
                print("Change username failed:", dto.get("message"))
                return False
        except Exception:
            return False

    def verify_blacklist(self):
        self._ensure_ready()
        payload = PayloadBuilder("checkblacklist") \
            .with_context(self._app_name, self._owner_id, self.session_id) \
            .with_value("hwid", HardwareIdentifier.fetch()) \
            .compile()
        resp = NetworkAgent.post(self._api_url, payload)
        try:
            dto = json.loads(resp)
            return dto.get("success", False)
        except Exception:
            return False

    def trigger_password_reset(self, username, email):
        self._ensure_ready()
        payload = PayloadBuilder("forgot") \
            .with_context(self._app_name, self._owner_id, self.session_id) \
            .with_value("username", username) \
            .with_value("email", email) \
            .compile()
        resp = NetworkAgent.post(self._api_url, payload)
        try:
            dto = json.loads(resp)
            return dto.get("success", False)
        except Exception:
            return False

    def apply_upgrade(self, username, license_key):
        self._ensure_ready()
        payload = PayloadBuilder("upgrade") \
            .with_context(self._app_name, self._owner_id, self.session_id) \
            .with_value("username", username) \
            .with_value("key", license_key) \
            .compile()
        resp = NetworkAgent.post(self._api_url, payload)
        try:
            dto = json.loads(resp)
            if dto.get("success"):
                print("Upgrade successful!")
                return True
            else:
                print("Upgrade failed:", dto.get("message"))
                return False
        except Exception:
            return False

    def transmit_chat_message(self, message, channel):
        self._ensure_ready()
        payload = PayloadBuilder("chatsend") \
            .with_context(self._app_name, self._owner_id, self.session_id) \
            .with_value("message", message) \
            .with_value("channel", channel) \
            .compile()
        resp = NetworkAgent.post(self._api_url, payload)
        try:
            dto = json.loads(resp)
            if dto.get("success"):
                return True
            print("Chat send failed:", dto.get("message"))
            return False
        except Exception:
            return False

    def retrieve_chat_history(self, channel):
        self._ensure_ready()
        payload = PayloadBuilder("chatget") \
            .with_context(self._app_name, self._owner_id, self.session_id) \
            .with_value("channel", channel) \
            .compile()
        resp = NetworkAgent.post(self._api_url, payload)
        try:
            dto = json.loads(resp)
            if dto.get("success"):
                return dto.get("messages", [])
            return []
        except Exception:
            return []

    def trigger_webhook(self, web_id, param, body, conttype):
        self._ensure_ready()
        payload = PayloadBuilder("webhook") \
            .with_context(self._app_name, self._owner_id, self.session_id) \
            .with_value("webid", web_id) \
            .with_value("params", param) \
            .with_value("body", body) \
            .with_value("conttype", conttype) \
            .compile()
        resp = NetworkAgent.post(self._api_url, payload)
        try:
            dto = json.loads(resp)
            if dto.get("success"):
                return dto.get("message")
            return None
        except Exception:
            return None

    def fetch_statistics(self):
        self._ensure_ready()
        payload = PayloadBuilder("fetchStats") \
            .with_context(self._app_name, self._owner_id, self.session_id) \
            .compile()
        resp = NetworkAgent.post(self._api_url, payload)
        try:
            dto = json.loads(resp)
            if dto.get("success"):
                self.app_info = dto.get("appinfo", {})
                return True
            return False
        except Exception:
            return False

    def terminate_session(self):
        self._ensure_ready()
        
        payload = PayloadBuilder("logout") \
            .with_context(self._app_name, self._owner_id, self.session_id) \
            .compile()

        resp = NetworkAgent.post(self._api_url, payload)
        try:
            dto = json.loads(resp)
        except Exception:
            return

        if not dto.get("success"):
            print("Logout failed:", dto.get("message"))
            return

        print("Logged out successfully!")
        self.session_id = ""
        self.initialized = False

    def get_formatted_user_info(self):
        if not self.current_user:
            return None

        data = self.current_user

        result = {
            "username": data.get("username"),
            "ip": data.get("ip"),
            "hwid": data.get("hwid"),
            "created": self._to_local(data.get("createdate")),
            "last_login": self._to_local(data.get("lastlogin")),
            "expires": self._to_local(data.get("expires")),
            "subscriptions": []
        }

        subs = data.get("subscriptions", [])

        for sub in subs:
            result["subscriptions"].append({
                "name": sub.get("subscription"),
                "expiry": self._to_local(sub.get("expiry")),
                "timeleft": self._format_timeleft(sub.get("timeleft"))
            })

        return result

    def _to_local(self, ts):
        if not ts:
            return "N/A"
        return datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d %I:%M:%S %p')

    def _format_timeleft(self, seconds):
        if not seconds:
            return "0d 0h 0m"

        seconds = int(seconds)
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60

        return f"{days}d {hours}h {minutes}m"


class PayloadBuilder:
    def __init__(self, action_type):
        self._payload = {"type": action_type}

    def with_context(self, app_name, owner_id, session_id):
        self._payload["name"] = app_name
        self._payload["ownerid"] = owner_id
        if session_id:
            self._payload["sessionid"] = session_id
        return self

    def with_value(self, key, value):
        if value is not None:
            self._payload[key] = value
        return self

    def compile(self):
        return self._payload


class NetworkAgent:
    @staticmethod
    def post(url, payload):
        try:
            response = requests.post(url, data=payload, timeout=10)
            return response.text
        except requests.exceptions.Timeout:
            print("Request timed out. Server may be down/slow.")
            return "{}"
        except Exception as e:
            print("Network error:", e)
            return "{}"


class HardwareIdentifier:
    @staticmethod
    def _hwid_to_sid(hwid):
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
    def fetch():
        system = platform.system()
        try:
            data = ""
            if system == "Windows":
                cpu = subprocess.check_output('powershell -Command "(Get-CimInstance Win32_Processor).ProcessorId"', shell=True).decode().strip()
                disk = subprocess.check_output('powershell -Command "(Get-CimInstance Win32_DiskDrive).SerialNumber"', shell=True).decode().strip()
                board = subprocess.check_output('powershell -Command "(Get-CimInstance Win32_BaseBoard).SerialNumber"', shell=True).decode().strip()
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

            hwid_hash = hashlib.sha256(data.encode()).hexdigest()
            return HardwareIdentifier._hwid_to_sid(hwid_hash)

        except Exception:
            return "UNKNOWN_HWID"


class SystemInfoCollector:
    @staticmethod
    def get_os_version():
        try:
            if platform.system() == "Windows":
                caption = subprocess.check_output('powershell -Command "(Get-CimInstance Win32_OperatingSystem).Caption"', shell=True).decode().strip()
                if caption.startsWith("Microsoft "):
                    caption = caption[len("Microsoft "):]
                version = subprocess.check_output('powershell -Command "(Get-CimInstance Win32_OperatingSystem).Version"', shell=True).decode().strip()
                return f"{caption} ({version})"
        except Exception:
            pass
        return f"{platform.system()} ({platform.version()})"

    @staticmethod
    def get_platform():
        return "native"

    @staticmethod
    def get_device_type():
        return "Desktop"

    @staticmethod
    def get_architecture():
        try:
            return os.environ.get("PROCESSOR_ARCHITECTURE", "X64").upper()
        except Exception:
            return "X64"

    @staticmethod
    def get_cpu_cores():
        try:
            if platform.system() == "Windows":
                cores = subprocess.check_output('powershell -Command "(Get-CimInstance Win32_Processor).NumberOfCores"', shell=True).decode().strip()
                threads = os.environ.get("NUMBER_OF_PROCESSORS", "2")
                if cores:
                    return f"{cores} Cores / {threads} Threads"
        except Exception:
            pass
        # Fallback
        import multiprocessing
        threads = multiprocessing.cpu_count()
        return f"{threads} Cores / {threads} Threads"

    @staticmethod
    def get_ram_gb():
        try:
            if platform.system() == "Windows":
                return subprocess.check_output('powershell -Command "[Math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB)"', shell=True).decode().strip()
        except Exception:
            pass
        return "0"
