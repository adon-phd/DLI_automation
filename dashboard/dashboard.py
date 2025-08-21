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
DLI_IP       = "DLI_IP_ADDRESS" # IP of the DLI switch - must be accessible from script location.
CLIENT_NAME  = "REGISTERED_CLIENT_NAME" # chosen during client registration
RAW_TOKEN    = "BASE64_TOKEN"  # generated during client registration
BEARER_TOKEN = f"{CLIENT_NAME}.{RAW_TOKEN}"
# ----------------------------------------

app = Flask(__name__, static_folder="static")

# Proxy helper
def dli_request(method, path, **kwargs):
    url = f"https://{DLI_IP}{path}"
    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {BEARER_TOKEN}"
    headers["X-CSRF"] = "x"
    return requests.request(method, url, headers=headers, verify=False, **kwargs)


# ---------------- ROUTES ----------------
@app.route("/")
def index():
    return send_from_directory("static", "ui.html")

@app.route("/api/<path:path>", methods=["GET", "POST", "PUT"])
def proxy(path):
    method = request.method
    data   = request.get_data()

    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "X-CSRF": "x"
    }

    # For outlet state changes, enforce correct content-type due to DLI requirements
    if method == "PUT" and data and path.endswith("/state/"):
        headers["Content-Type"] = "application/x-www-form-urlencoded"

    r = requests.request(
        method,
        f"https://{DLI_IP}/restapi/{path}",
        headers=headers,
        data=data,
        verify=False
    )
    return (r.content, r.status_code, r.headers.items())


# ----------------------------------------


if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) #Instal local cert to make more secure
    app.run(host="0.0.0.0", port=5440, debug=True) #CHANGE PORT AS REQUIRED (default is 5000)
