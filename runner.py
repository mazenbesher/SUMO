#!/usr/bin/env python
# http://sumo.dlr.de/wiki/TraCI/Interfacing_TraCI_from_Python

from __future__ import absolute_import
from __future__ import print_function

import sys, os, re, traceback

# we need to import python modules from the $SUMO_HOME/tools directory
try:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
    from sumolib import checkBinary
except ImportError:
    sys.exit(
        "please declare environment variable 'SUMO_HOME' as the root directory of your sumo installation (it should"
        " contain folders 'bin', 'tools' and 'docs')")

# start sumo-gui as server (as subprocess)
import subprocess

PORT = 8813
sumoBinary = checkBinary('sumo-gui')
sumoProcess = subprocess.Popen([sumoBinary, "-c", "cross/cross.sumo.cfg"
                                   , "--remote-port", str(PORT), "--start"], stdout=sys.stdout, stderr=sys.stderr)

# start traci and connect to sumo
import traci

MAX_STEPS = 3600
print("Connecting to the GUI on port ", PORT)
traci.init(PORT)


# simulate accident
def accident(vehID, accDistance):
    # slow down to zero
    # traci.vehicle.slowDown(vehID, speed=0, duration=100)

    # stop for the given duration
    # stop flags: 1 for parking, 2 for triggered, 3 for both
    traci.vehicle.setStop(vehID,
                          edgeID=traci.vehicle.getRoadID(vehID),
                          startPos=traci.vehicle.getLanePosition(vehID),
                          pos=traci.vehicle.getLanePosition(vehID) + accDistance,
                          laneIndex=traci.vehicle.getLaneIndex(vehID),
                          flags=2)



# regular expersions
reg_exp = {
    "step": re.compile("s(\d*)"),
    "color": re.compile("c(\d*)([r|b|g|y])"),
    "local_accident": re.compile("la(\d*) after(\d*)"),
    "temporal_accident": re.compile("ta(\d*) after(\d*) at(\d*)"),
    "resume": re.compile("r(\d*)"),
    "follow": re.compile("f(\d*)")
}

# array to hold temporal accidents
accidents = []  # (time_s, vehicle_id, distance)

# control the simulation
step = 0
while step < MAX_STEPS:
    try:
        command = input("(S)tep, (ID)s , (C)olor, (T)emporal \ (L)ocal (A)ccident, (F)ollow, (C)urrent (S)tep, (R)esume: ")

        # check if we need to make an accident
        for acc in accidents:
            if acc[0] == step:
                accident(acc[1], acc[2])

        # ----------------------------------------
        # step x
        if reg_exp["step"].match(command):
            # ex: s simulate one step
            # ex: s123 simulate till time 123
            match = reg_exp["step"].match(command)
            steps = match.group(1)
            if steps:
                steps = int(steps) * 1000
                # simulate steps
                traci.simulationStep(step + steps)
            else:
                # no number of steps passed -> one step
                traci.simulationStep()

        # ----------------------------------------
        # list vehicle id's
        elif command.lower() in ["i", "id"]:
            print(traci.vehicle.getIDList())

        # ----------------------------------------
        # print current step
        elif command.lower() == "cs":
            print(int(traci.simulation.getCurrentTime() / 1000))

        # ----------------------------------------
        # resume vehicle from stop
        elif reg_exp["resume"].match(command):
            # r11 -> resume vehicle with id 11
            match = reg_exp["resume"].match(command)
            vehID = match.group(1)
            try:
                traci.vehicle.resume(vehID)
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                print(''.join('!! ' + line for line in lines))

        # ----------------------------------------
        # track vehicle
        elif reg_exp["follow"].match(command):
            # ex: f11 -> follow vehicle with id 11
            match = reg_exp["follow"].match(command)
            vehID = match.group(1)
            viewID = traci.gui.getIDList()[0]
            traci.gui.trackVehicle(viewID, vehID)

        # ----------------------------------------
        # change color
        elif reg_exp["color"].match(command):
            # ex: c11r -> change color of vehecile with id 11 to red
            match = reg_exp["color"].match(command)
            id = match.group(1)
            color = match.group(2)
            if color == "r":
                traci.vehicle.setColor(id, (255, 0, 0, 0))
            elif color == "g":
                traci.vehicle.setColor(id, (0, 255, 0, 0))
            elif color == "b":
                traci.vehicle.setColor(id, (0, 0, 255, 0))
            elif color == "y":
                traci.vehicle.setColor(id, (255, 255, 0, 0))

        # ----------------------------------------
        # simulate accident
        elif reg_exp["local_accident"].match(command):
            # ex: a11 after123
            # simulate accident on vehicle with id 11 after 123 meters
            match = reg_exp["local_accident"].match(command)
            vehID = match.group(1)
            value = int(match.group(2))
            accident(vehID, value)

        elif reg_exp["temporal_accident"].match(command):
            # ex: a11 after123 at456
            # simulate accident on vehicle with id 11 after 123 meters at 456
            match = reg_exp["temporal_accident"].match(command)
            vehID = match.group(1)
            distance = int(match.group(2))
            time = int(match.group(3))
            accidents.append((time, vehID, distance))


        # ----------------------------------------
        # undefined command
        else:
            print("undefined command")

        # print new line
        print()

        # update step (in seconds)
        step = int(traci.simulation.getCurrentTime() / 1000)

    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        print(''.join('!! ' + line for line in lines))
        traci.close()

traci.close()
