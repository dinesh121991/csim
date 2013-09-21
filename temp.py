from random import shuffle
from Timing import *

def Sorter_random(L):
    if not (L==None or len(L)==0): 
        shuffle(L)
        return L
    else:
        return(L)

def Sorter_lpt(L):
    return(sorted(L,key=lambda j:-j.walltime))

def Sorter_ljf(L):
    return(sorted(L,key=lambda j:-j.cores))

def Sorter_ljfp(L):
    sortedjoblist=sorted(L,key=lambda j:-j.cores)
    newsortedjoblist=[]
    jcore=0
    jobs_buffer=[]
    for j in sortedjoblist:
        if j.cores==jcore:
            jobs_buffer.append(j)
        else:
            newsortedjoblist.extend(sorted(jobs_buffer,key=lambda j:-j.walltime))
            jobs_buffer=[j]
            jcore=j.cores
    newsortedjoblist.extend(sorted(jobs_buffer,key=lambda j:-j.walltime))
    return(newsortedjoblist)

def LocalAlgorithm_backfilling(env,hardware_status,campaign_queue,cores,sorter,logf):
    def logfunc(msg):
        return(logf('LOCALALGO '+msg))
    log=logfunc
    log('entering backfilling algorithm.')
    orders={}

    @print_timing(log)
    def compute_utilization(orders):
        augmentations=[(orders[j],j.cores) for j in orders]
        diminutions=[(orders[j]+j.get_remaining_walltime(),-j.cores) for j in orders]
        variations=sorted(augmentations+diminutions,key=lambda x:x[0])
        X=[] #abscisses
        Y=[] #ord.
        var=0
        for x,y in variations:
            var=var+y
            if x in X:
                i=X.index(x)
                Y[i]=var
            else:
                Y.append(var)
                X.append(x)
        return(X,Y)

    @print_timing(log)
    def find_first_hole(orders,walltime,size):
        if len(orders)==0:
            return 0
        X,Y=compute_utilization(orders)
        l=len(Y)
        for i in range(0,l):
            t,u=X[i],Y[i]
            if cores-u>=size:
                for k in range(i+1,l):
                    t2,u2=X[k],Y[k]
                        return(t)
                    if t2-t>=walltime:
                    if cores-u2<size:
                        break 
                    if k==l-1:
                        return(t)
        return(X[l-1])

    for j in hardware_status:
        orders[j]=0

    for c in campaign_queue:
        sortedjoblist=sorter([j for j in c.jobs if not j.started])
        for j in sortedjoblist:
            orders[j]=find_first_hole(orders,j.get_remaining_walltime(),j.cores)
    for j in hardware_status:
        del orders[j]
    return(orders)


def LocalAlgorithm_greedy(env,hardware_status,campaign_queue,cores,sorter,logf):
    def logfunc(msg):
        return(logf('LOCALALGO '+msg))
    log=logfunc
    log('entering backfilling algorithm.')
    orders={}
    #INPUT:
    #This function gets hardware_status and campaign_queue, as well as the number of cores in the system.
    #hardware_status is the list of jobs currently running on the system.
    #campaign_queue is the ordered list of campaigns to be scheduled in the system, post campaign scheduling decision.
    #OUTPUT:
    #this function must return a dict with the form job:starting time.
    #MISC:
    #the "sorter" argument is useless, we dont use it here (I still have it here because I did too much code factorisation at some point, sorry.)
    #log information with log("blah blah")and it will go to the main (csim_global.log) log along with timing info and correct headers, if you use the verbose option.

    for j in hardware_status:
        orders[j]=0

    hardware_status=sorted(hardware_status,key=lambda j:j.get_remaining_walltime())
    X=[0]+[j.get_remaining_walltime() for j in hardware_status] #abscisses
    Y0=sum([j.cores for j in hardware_status])
    Y=[Y0]
    yr=Y0
    for j in hardware_status:
        Y[j.get_remaining_walltime()]=yr-j.cores

    cq=[sorted([c.jobs],key=lambda j:j.cores) for c in campaign_queue]
    x=0
    while cq:
        joblist=cq[0]
        while joblist:
            hole=Y[x]
            found=False
            for i in joblist:
                if j.cores<hole:
                    orders[j]=x
                    joblist.remove(j)
                    found=True
                    break
            if found and not j.cores==hole:
                


        cq.pop(0)

