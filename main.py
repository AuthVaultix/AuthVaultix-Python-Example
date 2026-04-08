from authvaultix import api  

import sys
import time
import platform
import os
from time import sleep
from datetime import datetime, timezone

def clear():
    if platform.system() == 'Windows':
        os.system('cls & title Auth System Example')
    elif platform.system() == 'Linux':
        os.system('clear')
        sys.stdout.write("\033]0;Auth System Example\007")
        sys.stdout.flush()
    elif platform.system() == 'Darwin':
        os.system("clear && printf '\033[3J'")
        os.system('echo -n -e "\033]0;Auth System Example\007"')


print("Connecting...")

AuthVaultixapp = api(
    name="",
    ownerid="",
    secret="",
    version="1.0",
    api_url=""
)


def answer():
    try:
        print("""
1. Login
2. Register
3. License Key Only
        """)
        ans = input("Select Option: ")

        if ans == "1":
            user = input('Provide username: ')
            password = input('Provide password: ')
            return AuthVaultixapp.login(user, password)

        elif ans == "2":
            user = input('Provide username: ')
            password = input('Provide password: ')
            license = input('Provide License: ')
            return AuthVaultixapp.register(user, password, license)

        elif ans == "3":
            license = input('Enter your license: ')
            return AuthVaultixapp.license(license)

        else:
            print("\nInvalid option")
            sleep(1)
            clear()
            answer()

    except KeyboardInterrupt:
        os._exit(1)


answer()

# ===============================
# Display User Data (SAFE VERSION)
# ===============================

from datetime import timezone

data = AuthVaultixapp.user_data

# 🔒 Check if data exists
if not data:
    print("\nNo user data available - login or register first.")
    sleep(2)
    os._exit(1)

print("\nUser data:")

print("Username:", data.get("username", "N/A"))
print("IP address:", data.get("ip", "N/A"))
print("Hardware-Id:", data.get("hwid", "N/A"))

# 🔒 Safe subscriptions handling
subs = data.get("subscriptions", [])

if subs:
    for i, sub_data in enumerate(subs):
        sub = sub_data.get("subscription", "N/A")

        expiry_raw = sub_data.get("expiry")
        if expiry_raw:
            expiry = datetime.fromtimestamp(int(expiry_raw), timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        else:
            expiry = "N/A"

        timeleft = sub_data.get("timeleft", "N/A")

        print(f"[{i + 1} / {len(subs)}] | Subscription: {sub} - Expiry: {expiry} - Timeleft: {timeleft}")
else:
    print("No subscriptions found")

# 🔒 Safe created date
created_raw = data.get("createdate")
if created_raw:
    created = datetime.fromtimestamp(int(created_raw), timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
else:
    created = "N/A"

print("Created at:", created)

# 🔒 Last login
last_login = data.get("lastlogin")
if last_login:
    last_login_fmt = datetime.fromtimestamp(int(last_login), timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    print("Last login at:", last_login_fmt)
else:
    print("Last login at: First login")

# 🔒 Optional expires
expires_raw = data.get("expires")
if expires_raw:
    expires = datetime.fromtimestamp(int(expires_raw), timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    print("Expires at:", expires)

print("\nExiting in three seconds..")
sleep(3)
os._exit(1)
