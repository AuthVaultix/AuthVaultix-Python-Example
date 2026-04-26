from authvaultix import api
import sys
import platform
import os
from time import sleep

def clear():
    if platform.system() == 'Windows':
        os.system('Authvaultix Python-Example')
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
# CLEAN USER DATA DISPLAY
# ===============================

info = AuthVaultixapp.get_user_info()

if not info:
    exit_app("\nNo user data available - login first.")

print("\n=== User Data ===")
print("Username:", info["username"])
print("IP:", info["ip"])
print("HWID:", info["hwid"])
print("Created:", info["created"])
print("Last Login:", info["last_login"])

# Subscriptions
subs = info.get("subscriptions", [])

if subs:
    print("\nSubscriptions:")
    for i, sub in enumerate(subs):
        print(f"[{i+1}] {sub['name']} | Expiry: {sub['expiry']} | Timeleft: {sub['timeleft']}")
else:
    print("No subscriptions found")

exit_app("\nExiting in 3 seconds...", 3)