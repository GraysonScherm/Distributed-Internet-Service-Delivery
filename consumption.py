from __future__ import division


def load(lambdaList, lambdaNominal, serverID):
	serverPower = float(0)
	serverPowerIdle = float(63)
	serverPowerPeak = float(92)
	#will need to alter serverLoad input later
	serverLoad = float((lambdaList[serverID]) / lambdaNominal)

	serverPower = serverPowerIdle + ((serverPowerPeak - serverPowerIdle) * serverLoad)
	print (serverLoad)
	return serverPower

load([1000, 2003, 1905], 5000, 1)

    
    



