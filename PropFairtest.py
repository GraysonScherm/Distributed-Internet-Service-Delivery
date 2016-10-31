def Propfair(GEvector,Evector,lambdaList,T,NDC):
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

    return SClist

T=list([1,1,1])

Evector=[1]*3
SClist=[0]*3

#print len(GEvector)
GEvector=[2,1,1]


T=[1]*5
GEvector=[20,5,2,1,1]
Evector=[1]*5
SClist=[0]*5
lambdaList=[0]*5
for i in range(0,500):
 SClist,lambdaList, Metric=Propfair(GEvector,Evector,lambdaList,T)
