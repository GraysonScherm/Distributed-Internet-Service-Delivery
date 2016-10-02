def Propfair(GEvector,Evector,T):
    tc=5;
    Dvector=[GEvector/T for GEvector,T in zip(GEvector,T)] #metric vector for decision making
    MAX=Dvector.index(max(Dvector))
    SClist=[0]*len(GEvector) #refresh the Schedule list
    SClist[MAX]=1  #The Data Center which is selected
    print(SClist)
    for i in range(0,len(GEvector)):
        if SClist[i]==1:
            T[i]=(1-(1/tc))*T[i]+((1/tc))*GEvector[i]
        else:
            T[i]=(1-(1/tc))*T[i]
            
    return SClist
