def RoundRobin(SClist):
    if (1 in SClist)==False:
       SClist[0]=1
       return SClist
    elif (SClist.index(1))==(len(SClist)-1):
        SClist[SClist.index(1)]=0
        SClist[0]=1
        return SClist
    else:
       SClist[SClist.index(1)+1]=1;
       SClist[SClist.index(1)]=0;
       return SClist

SClist=[0]*3
for i in range(1,10):
 SClist=RoundRobin(SClist)
 print(SClist)
