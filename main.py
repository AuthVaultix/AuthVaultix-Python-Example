from authvaultix import api  

import sys
import time
import platform
import os
from time import sleep
from datetime import datetime, UTC

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


print("Initializing...")

AuthVaultixapp = api(
    name="test_app",
    ownerid="5d36476ca4",
    secret="7b9729387300a04a9a128f2dbe8a9b24659047ab7933ab312dfdca3d5397fb59",
    version="1.0",
    api_url="https://authvaultix.com/api/1.2/"  
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
            AuthVaultixapp.login(user, password)

        elif ans == "2":
            user = input('Provide username: ')
            password = input('Provide password: ')
            license = input('Provide License: ')
            AuthVaultixapp.register(user, password, license)

        elif ans == "3":
            license = input('Enter your license: ')
            AuthVaultixapp.license(license)

        else:
            print("\nInvalid option")
            sleep(1)
            clear()
            answer()

    except KeyboardInterrupt:
        os._exit(1)


answer()

# ===============================
# Display User Data
# ===============================

print("\nUser data:")
print("Username: " + str(AuthVaultixapp.user_data["username"]))
print("IP address: " + str(AuthVaultixapp.user_data["ip"]))
print("Hardware-Id: " + str(AuthVaultixapp.user_data["hwid"]))

subs = AuthVaultixapp.user_data["subscriptions"]

for i in range(len(subs)):
    sub = subs[i]["subscription"]
    expiry = datetime.fromtimestamp(int(subs[i]["expiry"]), UTC).strftime('%Y-%m-%d %H:%M:%S')
    timeleft = subs[i].get("timeleft", "N/A")
    print(f"[{i + 1} / {len(subs)}] | Subscription: {sub} - Expiry: {expiry} - Timeleft: {timeleft}")

print("Created at: " + datetime.fromtimestamp(int(AuthVaultixapp.user_data["createdate"]), UTC).strftime('%Y-%m-%d %H:%M:%S'))

if AuthVaultixapp.user_data.get("lastlogin"):
    print("Last login at: " + datetime.fromtimestamp(int(AuthVaultixapp.user_data["lastlogin"]), UTC).strftime('%Y-%m-%d %H:%M:%S'))
else:
    print("Last login at: First login")

# Expires field may not exist in response, so safer to check
if "expires" in AuthVaultixapp.user_data:
    print("Expires at: " + datetime.fromtimestamp(int(AuthVaultixapp.user_data["expires"]), UTC).strftime('%Y-%m-%d %H:%M:%S'))

print("\nExiting in three seconds..")
sleep(3)
os._exit(1)

