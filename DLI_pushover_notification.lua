--[[
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
]]

--[[
  DLI Notification Rule for Pushover Integration
  ----------------------------------------------

  This reference demonstrates how to send Pushover alerts from
  Digital Loggers (DLI) controllers running firmware 1.13.x.

  Usage:
    - In the DLI UI navigate to the "Event Notification" sidebar item
    - Create a WebHook notification target named "pushover"
      pointing to https://api.pushover.net/1/messages.json
      with content type "json".

    - In the Notification Rules UI:
        Condition: (see condition block below)
        Action:    (see action block below)

  Notes:
    - Replace YOUR_APP_TOKEN with the API Token of your Pushover app.
    - Replace YOUR_USER_KEY with your personal User Key from the
      Pushover dashboard.
    - The script_data table is populated by event.send() calls in Lua scripts.
    - This example expects script_data.outlet, script_data.new_state,
      and script_data.timestamp, but can be customized.
    - See associated power outlet automation in DLI_automation_script.lua
--]]

-- *** CONDITION ***
-- Condition block (paste into Condition field in the UI)
-- Matches any Lua script event
id=="dli.script.script_event"

-- *** ACTION ***
-- Action block (paste into Action field in the UI)
-- Constructs a Pushover payload and posts it via notify("pushover")
payload = {
  token   = "YOUR_APP_TOKEN",   -- from pushover.net application
  user    = "YOUR_USER_KEY",    -- from pushover dashboard
  title   = "DLI Scheduled Shutdown",
  message = string.format(
    "Outlet %s turned %s at %s",
    script_data.outlet or "?",
    script_data.new_state or "?",
    os.date("%Y-%m-%d %H:%M:%S", script_data.timestamp or os.time())
  ),
  priority = 0
}
notify("pushover")
