from __future__ import print_function
import sys
from dronekit import connect,VehicleMode
import time
import threading

# connection_string = "udp://:14550"
connection_string = ":14550"

vehicle = connect(connection_string,wait_ready=False)

time.sleep(2)

# for i in range(1,9):
#     ii = f'{i}'
#     print(f"Ch[{i}]: {vehicle.channels[ii]}")

# for i in range(10):
#     print(f"attitude: {vehicle.attitude}")
#     print(f"armed: {vehicle.armed}")
#     print(f"gps: {vehicle.gps_0}")
#     print(f"mode name: {vehicle.mode.name}")
#     print(f"is armable: {vehicle.is_armable}")
#     print(f"system status: {vehicle.system_status}")
#     print(f"Alt: {vehicle.location.global_relative_frame}")
#     time.sleep(1)


if vehicle.is_armable:
    vehicle.arm(wait=True)
else:
    print("Not armabled")
    sys.exit(0)

while not vehicle.armed:
    time.sleep(.3)

vehicle.mode = VehicleMode("STABILIZE")

time.sleep(1)

print("starting")
for i in range(100):
    vehicle.channels.overrides['3'] = 1300
    time.sleep(.1)


print("ended")
vehicle.disarm(True)

vehicle.close()