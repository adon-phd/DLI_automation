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
