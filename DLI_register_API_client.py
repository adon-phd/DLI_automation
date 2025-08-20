#!/usr/bin/env python3
"""
DLI Token Setup + Test Script
-----------------------------
- First run: generates token values, registers client, saves to <client>.json
- Later runs: loads token from <client>.json and reuses it
- --test-only switch: skips registration, only tests with saved token
- You will need the token later to make API calls in your application

***** The client auth requires the b64_token to be passed *****

***** DO NOT USE SPECIAL CHARACTERS IN CLIENT NAME *****

***** DO NOT CHANGE QUOTE STYLE *****

** Check the documentation for more permissions: https://www.digital-loggers.com/rest.html
** Using client tokens on DLI devices: https://www.digital-loggers.com/access_tokens.html

"""

import requests
import hashlib
import base64
import secrets
import json
import os
import sys
import argparse
from requests.auth import HTTPDigestAuth

# This will suppress a warning "InsecureRequestWarning: Unverified HTTPS request is being made to host '192.168.XXX.XXX'. 
# Adding certificate verification is strongly advised." Use at own risk or install the DLI cert.
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ---------------- CONFIG ----------------
DLI_IP = "LOCAL_IP"                # Your DLI IP - Must be reachable from where this script is running
ADMIN_USER = "USERNAME"            # Web UI username
ADMIN_PASS = "PASSWORD"            # Web UI password


OUTLET_SCOPES = {
    # Relay outlet states
    "/relay/outlets/all;/=name/": True,
    "/relay/outlets/all;/=state,transient_state,physical_state/?access=get": True,
    "/relay/outlets/all;/=state,transient_state/?access=modify": True,
    "/relay/outlets/all;/=cycle/?access=invoke": True,

    # Individual outlets (example: modify and cycle outlets 0-7)
    "/relay/outlets/=0,1,2,3,4,5,6,7;/=state,transient_state/?access=modify,get": True,
    "/relay/outlets/=0,1,2,3,4,5,6,7/=cycle/?access=invoke,get": True,

    # Bulk operations
    "/relay/set_outlet_transient_states/?access=modify": True,

    # Network settings
    "/network/wireless/enabled/?access=modify,get": True,

    # Script execution
    "/script/start/?access=invoke": True,
}
# ----------------------------------------

def make_token():
    """Generate raw phrase, SHA256 hash, and base64url form."""
    raw_phrase = secrets.token_urlsafe(12)[:16]  # 16-char phrase
    token_hash = hashlib.sha256(raw_phrase.encode()).hexdigest()
    b64url = base64.urlsafe_b64encode(raw_phrase.encode()).decode().rstrip("=")
    return raw_phrase, token_hash, b64url


def register_client(ip, client, token_hash, user, pw, scopes=None):
    """Register a client with the DLI controller using SHA256 hash as key."""
    if scopes is None:
        scopes = OUTLET_SCOPES

    url = f"https://{ip}/restapi/auth/clients/{client}/"
    data = {
        "name": client,
        "redirect_urls": {},
        "scopes": scopes,
        "refresh_tokens": {},
        "access_tokens": {token_hash: {}}
    }

    headers = {"X-CSRF": "x", "Content-Type": "application/json"}
    r = requests.put(
        url,
        headers=headers,
        data=json.dumps(data),
        verify=False,
        auth=HTTPDigestAuth(user, pw)
    )
    return r


def test_token(ip, client, b64_token):
    """Test by querying all outlet states."""
    url = f"https://{ip}/restapi/relay/outlets/all;/physical_state/"
    bearer = f"{client}.{b64_token}"
    headers = {
        "Authorization": f"Bearer {bearer}",
        "X-CSRF": "x",
        "Accept": "application/json"
    }

    print("\n[DEBUG] Equivalent curl command:")
    print(f"curl -D - -H 'Authorization: Bearer {bearer}' -k -H 'Accept:application/json' '{url}'\n")

    r = requests.get(url, headers=headers, verify=False)
    return r


def format_outlet_status(json_list):
    """Format [true/false,...] list into human-readable outlet states."""
    try:
        states = json.loads(json_list)
        if isinstance(states, list):
            lines = []
            for i, val in enumerate(states, start=1):
                status = "ON" if val else "OFF"
                lines.append(f"Outlet {i:2}: {status}")
            return "\n".join(lines)
    except Exception:
        pass
    return json_list


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-only", action="store_true", help="Skip registration, only test with saved token")
    args = parser.parse_args()

    client_name = input("Enter client name: ").strip()
    TOKEN_FILE = f"{client_name}.json"

    token_data = None

    if not args.test_only:
        if os.path.exists(TOKEN_FILE):
            choice = input(f"Token file {TOKEN_FILE} exists. Use existing (u) or delete and generate new (d)? [u/d]: ").strip().lower()
            if choice == "u":
                with open(TOKEN_FILE, "r") as f:
                    token_data = json.load(f)
            elif choice == "d":
                os.remove(TOKEN_FILE)
                print("Deleted old token file. A new one will be created.")
                token_data = None
            else:
                print("Invalid choice, exiting.")
                sys.exit(1)

        if token_data is None:
            raw_phrase, token_hash, b64_token = make_token()
            print(f"Raw phrase:   {raw_phrase}")
            print(f"SHA256 hash: {token_hash}")
            print(f"Base64url:   {b64_token}")

            print("\nRegistering client...")
            reg = register_client(DLI_IP, client_name, token_hash, ADMIN_USER, ADMIN_PASS)
            print("Register status:", reg.status_code, reg.text)

            token_data = {"client": client_name, "raw_phrase": raw_phrase, "hash": token_hash, "base64url": b64_token}
            with open(TOKEN_FILE, "w") as f:
                json.dump(token_data, f, indent=2)
            print(f"Token saved to {TOKEN_FILE}.")
    else:
        if not os.path.exists(TOKEN_FILE):
            print(f"Error: {TOKEN_FILE} not found. You must register first.")
            sys.exit(1)
        with open(TOKEN_FILE, "r") as f:
            token_data = json.load(f)

    # --- Test token ---
    print("\nTesting token...")
    b64_token = token_data["base64url"]
    resp = test_token(DLI_IP, client_name, b64_token)
    print("Status:", resp.status_code)
    print(format_outlet_status(resp.text))
