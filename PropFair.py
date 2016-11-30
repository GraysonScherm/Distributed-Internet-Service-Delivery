import os
import re
import sqlite3
import GEController 

def Propfair(GEvector,tVector):
    #green energy vector, Grid Energy vector , T is the previous scheduled memory
    tc=50
    NDC=len(GEvector)
    Metric=[0]*NDC    # Vector of the metric we used for scheduling
    for i in range(0,NDC):
        Metric[i]=GEvector[i]/tVector[i]
        
    MAX=Metric.index(max(Metric)) #the index of the choosen one  
    SClist=[0]*len(GEvector) #refresh the Schedule list
    SClist[MAX]=1  #The Data Center which is selected
    #for i in range(0,NDC):
    #    lambdaList[i]=lambdaList[i]+SClist[i]
    for i in range(0,NDC):
        if SClist[i]==1:
            tVector[i]=(1.0-(1.0/tc))*tVector[i]+((1.0/tc))*GEvector[i]
        else:
            tVector[i]=(1.0-(1.0/tc))*tVector[i]
    
    print("---------***T VALUE*****---------")
    print(tVector)
    #return SClist#, lambdaList
    return MAX, tVector
	
def fetchServerInfo():
       # serverInfo = re.split(';',line)
       # servers.append(serverInfo)
    fd = os.open("/soft/ryu/Distributed-Internet-Service-Delivery/controller.db", os.O_RDONLY)
    conn = sqlite3.connect('/dev/fd/%d' % fd)
    os.close(fd)
    cursor = conn.cursor()           
    currentEnergyValues = [0]*GEController.numberOfServers
    currentNumberOfUsers = [0]*GEController.numberOfServers
	
    for i in range(0, GEController.numberOfServers):
	cursor.execute("SELECT * from energyValues where id = (SELECT MAX(id) from energyValues where server  = ?)", str(i + 1))
	fetchedData = cursor.fetchall()
        if (fetchedData):
	  currentEnergyValues[i] = fetchedData[0][1]
        else:
	  currentEnergyValues[i] = 0
	  currentNumberOfUsers[i] = 0
          
	
	
    return currentEnergyValues, currentNumberOfUsers

		
	
