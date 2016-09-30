#consumption function
import sys

serverPower = float(0)
serverPowerIdle = float(sys.argv[1])
serverPowerPeak = float(sys.argv[2])
serverLoad = float(sys.argv[3])

serverPower = serverPowerIdle + ((serverPowerPeak - serverPowerIdle) * serverLoad)




