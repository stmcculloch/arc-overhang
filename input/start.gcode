G90 ; use absolute coordinates
M83 ; extruder relative mode
M104 S180 ; set extruder temp
M140 S60 ; set bed temp
M190 S60 ; wait for bed temp
M109 S180 ; wait for extruder temp
G28 W ; home all without mesh bed level
G80 ; mesh bed leveling
