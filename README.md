# DLI Automation


Basic automation and monitoring scripts for **Digital Loggers, Inc. (DLI) power controllers**.  
This repository provides tools to:

- Register API clients for secure token-based access.
- Automate power control via Lua scripts.
- Integrate notifications with **Pushover**.
- Control outlets via a simple web dashboard.

Perfect for remote astrophotography imaging systems.

---

## Getting Started

### 1. Register an API Client (Python)

Use `DLI_register_API_client.py` to securely create a REST API client on the controller.

- Generates a secure token.  
- Registers it via Digest authentication.  
- Saves credentials to `dli_token.json` for reuse.  

```bash
python3 DLI_register_API_client.py
```

### 2. Automate via Lua

Run `DLI_automation_script.lua` inside the DLI’s scripting environment web UI.  
This is suitable for scheduled or conditional power control tasks.

### 3. Get Notified with Pushover

Configure `DLI_pushover_notification.lua` with your Pushover API key to receive alerts when outlets change state. 
Paste into the DLI web UI under the notifications menu.

### 4. Web Dashboard Example

Navigate to the `dashboard/` directory and open `index.html` in a browser.  
This provides a simple outlet dashboard panel with async outlet toggling and pushover notifications.
Can disable outlets to prevent accidental, unrecoverable power outages.
Includes a single click button to start multiple outlets.

![DLI Outlet Control](./DLI%20Outlet%20Control.png)

---

## Security

This code is not production-ready.

- Credentials are hardcoded. Use environment variables or a secrets manager.  
- Certificate validation is disabled. Always verify TLS in production.  
- No authentication or authorization. Add proper access controls.  
- Commands may be sent over plaintext. Enforce HTTPS.  
- Input is not validated. Risk of injection or misuse.  
- Debug logs may leak sensitive info. Remove before deployment.  
- No rate limiting or brute-force protection.  
- No audit logging of sensitive actions.
- Remote access is not secured. If the DLI device is at a remote site, use a secure VPN (e.g. WireGuard, ZeroTier) or similar tunneling solution.   

Use this only as a proof of concept. A secure deployment requires proper secret handling, TLS, authentication, and logging.



---

## License

This project is released under a **Non-Commercial License**.  

You may use, modify, and share this code for personal, educational, or research purposes,  
provided that all use remains **non-commercial** and attribution is provided.

The following activities are not permitted without prior written permission:  
- Use of this code, in whole or in part, for commercial purposes, including incorporation into proprietary products or services.  
- Use of this code or derivative works for training or fine-tuning machine learning or artificial intelligence models.  


[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Lua](https://img.shields.io/badge/Lua-5.1+-green.svg)](https://www.lua.org/)
[![License: NC](https://img.shields.io/badge/License-Non--Commercial-red.svg)](./LICENSE)
