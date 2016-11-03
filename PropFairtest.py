def Propfair(GEvector,Evector,lambdaList,T):
    #green energy vector, Grid Energy vector , T is the previous scheduled memory
    tc=50
    NDC=len(GEvector)
    Metric=[0]*NDC    # Vector of the metric we used for scheduling
    for i in range(0,NDC):
        Metric[i]=GEvector[i]/T[i]
        
    MAX=Metric.index(max(Metric)) #the index of the choosen one
    SClist=[0]*len(GEvector) #refresh the Schedule list
    SClist[MAX]=1  #The Data Center which is selected
    for i in range(0,NDC):
        lambdaList[i]=lambdaList[i]+SClist[i]
    for i in range(0,NDC):
        if SClist[i]==1:
            T[i]=(1-(1/tc))*T[i]+((1/tc))*GEvector[i]
        else:
            T[i]=(1-(1/tc))*T[i]
            
    print(T)
    print(Metric)
    print(MAX)
    print(SClist)
    print(lambdaList)
    print('----------------')
    return SClist, lambdaList, Metric, T

T=[1]*3
GEvector=[82,95,54]
Evector=[1]*3
SClist=[0]*3
lambdaList=[0]*3
for i in range(0,10):
 SClist,lambdaList, Metric, T=Propfair(GEvector,Evector,lambdaList,T)

x=input()
