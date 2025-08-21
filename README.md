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

## License

This project is released under a **non-commercial license**.  
You may use, modify, and share the code for personal or research purposes,  
but **commercial use is prohibited without explicit permission**.


[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Lua](https://img.shields.io/badge/Lua-5.1+-green.svg)](https://www.lua.org/)
[![License: NC](https://img.shields.io/badge/License-Non--Commercial-red.svg)](./LICENSE)
