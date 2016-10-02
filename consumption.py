#consumption function
import sys


def main():
	serverPower = float(0)
	serverPowerIdle = float(63)
	serverPowerPeak = float(92)
	#will need to alter serverLoad input later
	serverLoad = float(sys.argv[1])

	serverPower = serverPowerIdle + ((serverPowerPeak - serverPowerIdle) * serverLoad)

	return serverPower


    
    



