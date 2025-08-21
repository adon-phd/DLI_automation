# ------------------------------------------------------------------------------
# Copyright (c) 2025 Adon Phillips
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to use,
# copy, modify, and merge the Software for non-commercial purposes only,
# including academic and personal projects, subject to the following conditions:
#
# 1. The above copyright notice and this permission notice shall be included in
#    all copies or substantial portions of the Software.
# 2. Commercial use of the Software, in whole or in part, is strictly prohibited
#    without prior written permission from the copyright holder.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# ------------------------------------------------------------------------------

#!/usr/bin/env python3
import os
import requests
from flask import Flask, request, jsonify, send_from_directory

# ---------------- CONFIG ----------------

# DLI Client settings - CHANGE TO ADD YOUR VALUES
DLI_IP       = "DLI_IP_ADDRESS" # IP of the DLI switch - must be accessible from script location.
CLIENT_NAME  = "REGISTERED_CLIENT_NAME" # chosen during client registration
RAW_TOKEN    = "BASE64_TOKEN"  # generated during client registration
BEARER_TOKEN = f"{CLIENT_NAME}.{RAW_TOKEN}"

# Pushover settings - CHANGE TO ADD YOUR VALUES
PUSHOVER_API  = "https://api.pushover.net/1/messages.json"
PUSHOVER_APP  = os.getenv("PUSHOVER_APP_TOKEN", "YOUR_APP_TOKEN")
PUSHOVER_USER = os.getenv("PUSHOVER_USER_KEY", "YOUR_USER_KEY")
# ----------------------------------------


app = Flask(__name__, static_folder="static")


# ---------------- HELPERS ----------------
def dli_request(method, path, **kwargs):
    url = f"https://{DLI_IP}{path}"
    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {BEARER_TOKEN}"
    headers["X-CSRF"] = "x"
    return requests.request(method, url, headers=headers, verify=False, **kwargs)


def send_pushover(title, message, priority=0):
    """Send a Pushover notification."""
    if not PUSHOVER_APP or not PUSHOVER_USER:
        print("Pushover not configured.")
        return
    try:
        payload = {
            "token": PUSHOVER_APP,
            "user": PUSHOVER_USER,
            "title": title,
            "message": message,
            "priority": priority,
        }
        r = requests.post(PUSHOVER_API, data=payload, timeout=5)
        print("Response:", r.status_code, r.text)  # <-- add this
        r.raise_for_status()
        print(f"Pushover sent: {title} - {message}")
    except Exception as e:
        print(f"Failed to send pushover: {e}")


# ---------------- ROUTES ----------------
@app.route("/")
def index():
    return send_from_directory("static", "control.html")


@app.route("/api/<path:path>", methods=["GET", "POST", "PUT"])
def proxy(path):
    method = request.method
    data   = request.get_data()

    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "X-CSRF": "x"
    }


    # Detect outlet state changes
    is_outlet_state_change = (method == "PUT" and data and path.endswith("/state/"))

    if is_outlet_state_change:
        headers["Content-Type"] = "application/x-www-form-urlencoded"

    r = requests.request(
        method,
        f"https://{DLI_IP}/restapi/{path}",
        headers=headers,
        data=data,
        verify=False
    )

    # Detect outlet state or cycle changes
    is_outlet_action = (
        method in ("PUT", "POST")   # state = PUT, cycle = POST
        and (path.endswith("/state/") or path.endswith("/cycle/"))
    )


    if is_outlet_action:
        parts = path.strip("/").split("/")   # ['relay','outlets','4','state'] or ['relay','outlets','4','cycle']

        try:
            api_index = int(parts[2])        # API index (0-based)
            outlet_id = api_index + 1        # Convert to UI numbering (1-based)
        except (IndexError, ValueError):
            outlet_id = "?"

        raw_val = data.decode().strip().lower() if data else ""

        if path.endswith("/cycle/"):
            status_text = "CYCLED (OFF → ON)"
        elif raw_val in ("1", "value=1", "true", "value=true"):
            status_text = "turned ON"
        elif raw_val in ("0", "value=0", "false", "value=false"):
            status_text = "turned OFF"
        else:
            status_text = f"UNKNOWN({raw_val})"

        send_pushover(
            "DLI Outlet Change",
            f"Outlet {outlet_id} {status_text}"
        )




    return (r.content, r.status_code, r.headers.items())


# ---------------- MAIN ----------------
if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    app.run(host="0.0.0.0", port=5440, debug=True)
