def Propfair(GEvector,Evector,T):
    tc = float(5)
    Dvector=[GEvector/T for GEvector,T in zip(GEvector,T)] #metric vector for decision making
    T=list([1,1,1])
    MAX=Dvector.index(max(Dvector))
    SClist=[0,0,0]#*len(GEvector) #refresh the Schedule list
    SClist[MAX]=1  #The Data Center which is selected
    print(SClist)
    for i in range(0,3): #len(GEvector)):
	if SClist[i]==1:
  	  h=float(T[i])
           # T[i]=((1-(1/tc))*T[i])+(((1/tc))*GEvector[i])
	  h=float((1-(1/tc)))*float(h)	
        else:
            T[i]=(1-(1/tc))*T[i]

        
    print(T)
    print(MAX)
    print(SClist)
    return SClist

T=list([1,1,1])

Evector=[1]*3
SClist=[0]*3

#print len(GEvector)
GEvector=[2,1,1]

for i in range(0,10):
 SClist=Propfair(GEvector,Evector,T)
