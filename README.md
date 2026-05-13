<div align="center">

# 🔐 AuthVaultix Python SDK

**The official Python client library for [AuthVaultix](https://authvaultix.com) — a powerful license & authentication management platform.**

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![AuthVaultix](https://img.shields.io/badge/Powered%20by-AuthVaultix-purple?style=for-the-badge)](https://authvaultix.com)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey?style=for-the-badge)]()

</div>

---

## 📖 Table of Contents

- [What is AuthVaultix?](#-what-is-authvaultix)
- [Features](#-features)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Full Example (main.py)](#-full-example-mainpy)
- [API Reference](#-api-reference)
- [HWID Detection](#-hwid-detection)
- [User Data Structure](#-user-data-structure)
- [Error Handling](#-error-handling)
- [License](#-license)

---

## 🔐 What is AuthVaultix?

**AuthVaultix** is a cloud-based software licensing and user authentication system. This Python SDK allows your application to seamlessly connect to the AuthVaultix API to:

- Authenticate users via **login**, **registration**, or **license key**
- Protect your software with **hardware-locked licensing (HWID)**
- Retrieve **user subscriptions**, metadata, and custom variables
- Prevent **unauthorized access** and piracy

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔑 **Login / Register** | Authenticate users with username & password |
| 🪪 **License Key Auth** | Allow access via license key only |
| 🖥️ **HWID Locking** | Hardware fingerprinting on Windows, Linux & macOS |
| 📦 **Subscription Info** | Retrieve active subscriptions with expiry & time left |
| 🔢 **Custom Variables** | Get/Set server-side variables per user |
| 🚪 **Secure Logout** | Invalidate session server-side |
| ⚡ **Session Management** | Auto session-ID handling on init |

---

## 📋 Requirements

- Python **3.7+**
- `requests` library

Install dependencies:

```bash
pip install requests
```

---

## 🚀 Installation

**Option 1: Clone the repository**

```bash
git clone https://github.com/AuthVaultix-Python-Example.git
cd authvaultix-python
pip install requests
```

**Option 2: Download manually**

Download `authvaultix.py` and place it in your project directory.

---

## ⚡ Quick Start

```python
from authvaultix import AuthVaultixClient

# Initialize the client
client = AuthVaultixClient(
    app_name="MyApp",
    owner_id="your_owner_id_here",
    secret="your_secret_key_here",  # Must be 64+ characters
    version="1.0",
    api_url="https://authvaultix.com/api/1.0/"
)

# Login
success = client.login("myusername", "mypassword")

if success:
    info = client.get_user_info()
    print("Welcome,", info["username"])
    print("Subscription expires:", info["subscriptions"][0]["expiry"])
```

---

## 📄 Full Example (main.py)

The included `main.py` demonstrates a complete authentication flow with a console menu:

```python
from authvaultix import AuthVaultixClient

AuthVaultixapp = AuthVaultixClient(
    app_name="",           # Your app name from dashboard
    owner_id="",           # Your Owner ID from dashboard
    secret="",             # Your Secret key (64+ chars)
    version="1.0",
    api_url="https://authvaultix.com/api/1.0/"
)

# 1. Login
AuthVaultixapp.login("username", "password")

# 2. Register
AuthVaultixapp.register("username", "password", "LICENSE-KEY-HERE", "email@example.com")

# 3. License key only
AuthVaultixapp.license_login("LICENSE-KEY-HERE")

# Get user info after auth
info = AuthVaultixapp.get_user_info()
print("Username:", info["username"])
print("HWID:", info["hwid"])
print("IP:", info["ip"])

for sub in info["subscriptions"]:
    print(f"Sub: {sub['name']} | Expires: {sub['expiry']} | Left: {sub['timeleft']}")
```

---

## 📚 API Reference

### `AuthVaultixClient(app_name, owner_id, secret, version, api_url)`

Initializes and connects your app to the AuthVaultix server.

| Parameter | Type | Description |
|---|---|---|
| `app_name` | `str` | Your application name |
| `owner_id` | `str` | Owner ID from dashboard (min 10 chars) |
| `secret` | `str` | Secret key from dashboard (min 64 chars) |
| `version` | `str` | Your app version (e.g. `"1.0"`) |
| `api_url` | `str` | API endpoint URL |

---

### Authentication Methods

#### `login(username, password)`
Authenticates a user with username and password. Returns `True` on success.

#### `register(username, password, license_key, email="")`
Registers a new user using a license key and optional email. Returns `True` on success.

#### `license_login(license_key)`
Authenticates a user using a license key only (no username/password). Returns `True` on success.

#### `logout()`
Logs the user out and invalidates the current session.

---

### User & Session Management

#### `get_user_info()`
Returns a dictionary with the authenticated user's information.

#### `check()`
Validates if the current session is still active. Returns `True` if valid.

#### `upgrade(username, license_key)`
Upgrades a user's account/subscription with a new license key.

#### `forgot_password(username, email)`
Triggers a password reset email for the given user.

#### `change_username(new_username)`
Changes the authenticated user's username.

---

### Variables & Data

#### `get_var(var_name)`
Fetches a user-specific server-side variable.

#### `set_var(var_name, value)`
Sets a user-specific server-side variable for the current user.

#### `get_global_var(var_key)`
Fetches a global server-side variable by its ID.

#### `download(file_id)`
Downloads a secure file from the server. Returns the file's binary content.

---

### Security & Logging

#### `log(message)`
Sends a log message to the AuthVaultix dashboard.

#### `fetch_online()`
Retrieves a list of currently online clients.

#### `ban(reason="")`
Bans the currently authenticated user with an optional reason.

#### `check_blacklist()`
Checks if the current machine's HWID is blacklisted on the server. Returns `True` if blacklisted.

#### `fetch_stats()`
Fetches application statistics (users, active, etc.) into `app_info`.

---

### Communication & Webhooks

#### `chat_send(message, channel)`
Sends a message to a specific chat channel.

#### `chat_fetch(channel)`
Retrieves chat history for a specific channel.

#### `webhook(web_id, param, body="", conttype="")`
Triggers a custom webhook on the AuthVaultix server.

---

## 🖥️ HWID Detection

The SDK automatically generates a unique Hardware ID (HWID) for each machine and locks the license to it. It supports:

| Platform | Sources Used |
|---|---|
| **Windows** | CPU Processor ID + Disk Serial + Motherboard Serial + Machine GUID |
| **Linux** | `/etc/machine-id` + CPU Serial + Disk Serial |
| **macOS** | Hardware Serial Number |

The raw hardware data is hashed with **SHA-256** and converted to a **Windows SID-style format** (e.g. `S-1-5-21-XXXX-XXXX-XXXX-XXXX`).

You can also get the HWID manually:

```python
from authvaultix import HardwareIdentifier

hwid = HardwareIdentifier.fetch()
print("Your HWID:", hwid)
```

---

## 📦 User Data Structure

After a successful login/register/license, `get_user_info()` returns:

```python
{
    "username": "john_doe",
    "ip": "123.456.789.0",
    "hwid": "S-1-5-21-XXXX-XXXX-XXXX-XXXX",
    "created": "2024-01-15 10:30:00 AM",
    "last_login": "2024-06-01 08:00:00 AM",
    "expires": "2025-01-15 10:30:00 AM",
    "subscriptions": [
        {
            "name": "premium",
            "expiry": "2025-01-15 10:30:00 AM",
            "timeleft": "215d 14h 30m"
        }
    ]
}
```

---

## ⚠️ Error Handling

The SDK prints descriptive error messages to the console. Common errors:

| Error | Cause |
|---|---|
| `Invalid ownerid` | `ownerid` is missing or less than 10 characters |
| `Invalid secret` | `secret` is missing or less than 64 characters |
| `Invalid API URL` | `api_url` doesn't start with `http` |
| `Init failed` | App not found or version mismatch in dashboard |
| `Login failed` | Wrong credentials or HWID mismatch |
| `Request timed out` | Server is down or network issue |

---

## 🗂️ Project Structure

```
📦 authvaultix-python/
 ┣ 📄 authvaultix.py   ← Core SDK (import this in your project)
 ┣ 📄 main.py          ← Full usage example with console menu
 ┗ 📄 README.md        ← You are here
```

---

## 📜 License

This project is licensed under the **MIT License** — you are free to use, modify, and distribute it.

---

<div align="center">

**Made with ❤️ for the AuthVaultix community**

[🌐 Website](https://authvaultix.com) • [📧 Support](mailto:support@authvaultix.com)

</div>
