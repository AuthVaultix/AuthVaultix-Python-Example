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
    else:
        os.system('clear')

def exit_app(msg="", delay=2):
    if msg:
        print(msg)
    sleep(delay)
    sys.exit()

print("Connecting...")

AuthVaultixapp = api(
    name="",
    ownerid="",
    secret="",
    version="1.0",
    api_url="https://authvaultix.com/api/1.0/"
)

def auth_menu():
    while True:
        try:
            print("""
1. Login
2. Register
3. License Key Only
            """)
            ans = input("Select Option: ").strip()

            if ans == "1":
                user = input('Username: ')
                password = input('Password: ')
                return AuthVaultixapp.login(user, password)

            elif ans == "2":
                user = input('Username: ')
                password = input('Password: ')
                license = input('License: ')
                return AuthVaultixapp.register(user, password, license)

            elif ans == "3":
                license = input('Enter License: ')
                return AuthVaultixapp.license(license)

            else:
                print("Invalid option\n")
                sleep(1)
                clear()

        except KeyboardInterrupt:
            exit_app("\nUser exited.")

# Run auth
auth_menu()

# ===============================
# Display User Data
# ===============================

data = AuthVaultixapp.user_data

if not data:
    exit_app("\nNo user data available - login first.")

print("\n=== User Data ===")

print("Username:", data.get("username", "N/A"))
print("IP Address:", data.get("ip", "N/A"))
print("HWID:", data.get("hwid", "N/A"))

# Subscriptions
subs = data.get("subscriptions", [])

from datetime import datetime

def to_local(ts):
    return datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d %I:%M:%S %p')

def format_timeleft(seconds):
    seconds = int(seconds)
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    return f"{days}d {hours}h {minutes}m"

# =====================

if subs:
    print("\nSubscriptions:")
    for i, sub_data in enumerate(subs):
        sub = sub_data.get("subscription", "N/A")

        expiry_raw = sub_data.get("expiry")
        expiry = to_local(expiry_raw) if expiry_raw else "N/A"

        timeleft_raw = sub_data.get("timeleft", 0)
        timeleft = format_timeleft(timeleft_raw)

        print(f"[{i+1}] {sub} | Expiry: {expiry} | Timeleft: {timeleft}")
else:
    print("No subscriptions found")

# Created Date
created_raw = data.get("createdate")
created = (
    datetime.fromtimestamp(int(created_raw), timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    if created_raw else "N/A"
)
print("Created at:", created)

# Last Login
last_login = data.get("lastlogin")
if last_login:
    last_login_fmt = datetime.fromtimestamp(int(last_login), timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    print("Last login:", last_login_fmt)
else:
    print("Last login: First time")

# Optional Expiry
expires_raw = data.get("expires")
if expires_raw:
    expires = datetime.fromtimestamp(int(expires_raw), timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    print("Expires at:", expires)

exit_app("\nExiting in 3 seconds...", 3)