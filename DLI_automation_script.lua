--[[
# ------------------------------------------------------------------------------
# Copyright (c) 2025 adon-phd
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
  *** OUTLET POWER OFF SCHEDULING ***
  Runs indefinitely, turning off all outlets in the `outlets` list every day at 7:55 AM.
  For each outlet:
    - Records its previous state (ON/OFF).
    - Turns it OFF.
    - Logs the change.
  After processing all outlets, sends one summary event with the list of outlets shut down. 
  The event is picked up by the DLI notification system and delivered to the configured recipient.
]]

function turn_off_outlets_daily()
  while true do
    wait_until({hour=7, min=55}) -- power-off at 07:55

    local shut = {}
    for _, n in ipairs(outlets) do
      local prev = outlet[n].state and "ON" or "OFF"
      outlet[n].off()
      table.insert(shut, string.format("%d(was %s)", n, prev))
      log.notice(string.format("Outlet %d turned OFF (was %s)", n, prev))
    end

    -- Send one combined event
    event.send("Scheduled shutdown", {
      outlets = table.concat(shut, ", "),
      new_state = "OFF",
      timestamp = os.time()
    })

    delay(60) -- prevent multiple events
  end
end


-- ****** Testing Functions ******
--[[
  This function does not alter real scheduling behaviour; it only creates 
  a one-off test event and writes a log entry for visibility.
]]

function pushover_test()
  event.send("Scheduled shutdown", {
    outlet = 4,
    previous_state = "ON",
    new_state = "OFF",
    timestamp = os.time()
  })
  log.notice("Test event sent for outlet 4")
end 
