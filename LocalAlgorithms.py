from random import shuffle
from Timing import *

def schedule_batch_of_jobs(jobs,utilization,cores,log): 
    #modify the orders to schedule c on the system in a greedy fashion.
    return_orders={}
    jobs=sorted(jobs,key=lambda j:-j.cores)
    i=0
    x=utilization[0][0]
    while jobs:
        hole=cores-get_utilization_value(log,x,utilization)
        found=False
        for j in jobs:
            if does_it_fit(log,x,j,utilization,cores):
                jobs.remove(j)
                update_utilization(log,x,j,utilization)
                return_orders[j]=x
                found=True
                break
        if found:
            hole=cores-get_utilization_value(log,x,utilization)
            if not hole>0:
                i=min([h for h,k in enumerate(utilization) if k[0]>x])
                x=utilization[i][0]
            else:
                log(utilization)
                i=min([h for h,k in enumerate(utilization) if k[0]>=x])
                x=utilization[i][0]
        else:
            i=min([h for h,k in enumerate(utilization) if k[0]>x])
            x=utilization[i][0]
    return(return_orders)

def get_utilization_value(log,x,utilization):
    log("ohaigetutvalinside")
    #utilization supposed sorted.
    j=utilization[0][0]
    for i in range(0,len(utilization)):
        log("ohaigetutvalinside2 and i is  %s" %i)
        if utilization[i][0]<x:
            j=i
        elif utilization[i][0]==x:
            return(utilization[i][1])
        else :
            return(utilization[j][1])

def does_it_fit(log,t,job,utilization,cores):
    #does job j fit into the utilization graph at t?
    log("does_it_fit call: t %s job %s utilization %s cores %s"%(t,job,utilization,cores))
    t_index=[x for x,y in enumerate(utilization) if y[0]==t]
    log("t_index %s"%(t_index))
    y=job.cores
    x=job.get_remaining_walltime() #TODO simplify
    if cores-utilization[t_index[0]][1]<y:
        return(False)
    
    log("t_index is %s and len(utilization) is %s" %(t_index,len(utilization)))
    for i in range(t_index[0]+1,len(utilization)):
        if utilization[i][0]-t>=x:
            return(True)
        elif cores-utilization[i][1]<y:
            return(False)
    return(True)

def update_utilization(log,t,job,utilization):
    #log("update_utilization call on job %s with utilization %s at time %s" %(job,utilization,t))
    #update X Y to account for job j being scheduled at time t
    t_index=[x for x,y in enumerate(utilization) if y[0]==t]
    cores=job.cores
    size=job.get_remaining_walltime() #TODO simplify
    
    #log("t_index : %s, cores: %s, size: %s"%(t_index,cores,size))
    passed_job=False
    done=False
    for i in range(0,len(utilization)):
        #log("i is %s"%i)
        x,y=utilization[i]
        if x>=t and x<t+size:
            #log("1")
            passed_job=True
            BAK=utilization[i][1]
            utilization[i][1]+=cores
        elif x==t+size:
            #log("2")
            done=True
            break
        elif passed_job:
            #log("OEUOEU 3")
            utilization.append([t+size,BAK])
            done=True
            break
    if not done:
        #print("notdone")
        utilization.append([t+size,0])
    utilization.sort(key=lambda tup:tup[0])
    #log("update_utilization: before useless values removal: %s" %utilization)
    y=utilization[0][1]
    i=1
    L=len(utilization)
    while i<L:
        y2=utilization[i][1]
        if y==y2:
            utilization.pop(i)
            L-=1
        else:
            i+=1
        y=y2
    #log("update_utilization: after useless values removal: %s" %utilization)



def LocalAlgorithm_greedy(env,hardware_status,campaign_queue,cores,sorter,logf):
    def logfunc(msg):
        return(logf('LOCALALGO '+str(msg)))
    log=logfunc
    log("entering greedy algorithm")
    #log('entering backfilling algorithm.')
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
    #log(hardware_status)

    hardware_status=sorted(hardware_status,key=lambda j:j.get_remaining_walltime())
    y=sum([j.cores for j in hardware_status if not j.get_remaining_walltime()==0])
    utilization=[[0,y]]
    #log("before computing orders, hwstatus: %s" %hardware_status)
    last=0
    for j in hardware_status:
        if not j.get_remaining_walltime()==0:
            y=y-j.cores
            #log("DADADA remaining walltime for job %s is %s" %(j,j.get_remaining_walltime()))
            current=j.get_remaining_walltime()
            #log('last %s'%current)
            #log('current %s'%current)
            if last==current:
                utilization[-1][1]=y
            else:
                log("err1")
                utilization.append([j.get_remaining_walltime(),y])
                log("err2")
            last=current
    if len(utilization)==1 and not len(hardware_status) ==0:
        utilization=[[0,0]]

    #log("and resulting utilization: %s" %utilization)
    for c in campaign_queue:
        #log("CALLING SCHEDULE_BATCH_OF_JOBS on campaign %s and utilization is %s"%(c.cid,utilization))
        log("err3")
        neworders=schedule_batch_of_jobs([j for j in c.jobs if not j.started],utilization,cores,log)
        log("err4")
        #log("EXTENDING ORDERS %s with orders %s and utilization is %s"%(orders,neworders,utilization))
        orders=dict(orders.items()+neworders.items())
    
    #log("----------------RETURN_ORDERS:--------------------__")
    #log("--------------------------------------------------__")
    log("exiting greedy algorithm with orders")
    return(orders)

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
                    if t2-t>=walltime:
                        return(t)
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

